#!/usr/bin/env perl

#-----------------------------------------------------------------------
# Perl Emoji Replacer Hook - MANUAL JSON
# Description: Replaces g/G with giraffe emoji and h/H with hamster emoji AFTER editing
# Priority: 80
# Category: editing_ops
# Type: post_edit
# Copyright (C) 2025 Peter Leukanič
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
#-----------------------------------------------------------------------

use strict;
use warnings;
use utf8;

binmode STDOUT, ":encoding(UTF-8)";
binmode STDIN, ":encoding(UTF-8)";

# Read JSON from STDIN
my $context_json = do { local $/; <STDIN> };

# Basic validation
exit 0 unless defined $context_json && length($context_json) > 0;

eval {
    require JSON::PP;
    
    my $decoder = JSON::PP->new->utf8;
    my $context = $decoder->decode($context_json);
    
    # Process only POST_EDIT actions
    if ($context->{'action'} && $context->{'action'} eq 'post_edit') {
        my $text = $context->{'new_text'} // '';
        
        if (defined $text && $text ne '') {
            # Perform case-insensitive replacement
            $text =~ s/g/🦒/gi;
            $text =~ s/h/🐹/gi;
        }
        
        # Escape quotes and backslashes in the text
        $text =~ s/"/\\"/g;
        $text =~ s/\\/\\\\/g;
        
        # Print manually constructed JSON
        print "{\"new_text\":\"$text\"}\n";
        exit 0;
    }
};

exit 0;
