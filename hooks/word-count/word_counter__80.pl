#!/usr/bin/env perl

#-----------------------------------------------------------------------
# Perl Word Counter Hook
# Description: Counts words, lines, and characters in files using Perl 5
# Priority: 80
# Copyright (C) 2025 Peter Leukanič
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
#-----------------------------------------------------------------------

use strict;
use warnings;

sub main {
    # Get JSON from command line argument or STDIN
    my $context_json;
    if (@ARGV > 0) {
        $context_json = $ARGV[0];
    } else {
        $context_json = do { local $/; <STDIN> };
    }
    
    # Basic check
    return undef unless defined $context_json && length($context_json) > 0;
    
    # Try to decode JSON
    eval {
        require JSON::PP;
        my $decoder = JSON::PP->new->utf8;
        my $context = $decoder->decode($context_json);
        
        # Check if this is a word count request
        if ($context->{'action'} && $context->{'action'} eq 'count_words') {
            my $text = $context->{'file_content'} // '';
            my $filename = $context->{'filename'} // 'unknown';
            
            # More precise counting
            my $line_count = () = $text =~ /\n/g;  # Count newlines
            $line_count++ if length($text) > 0 && $text !~ /\n$/;  # Add 1 if no trailing newline
            
            # More wc-like word counting
            my $word_count = 0;
            $word_count++ while $text =~ /\S+/g;
            
            my $char_count = length($text);
            
            # Output results to STDOUT
            print "\n" . '*' x 60 . "\n";
            print "$filename contains (Perl hook):\n";
            print "- $word_count words\n";
            print "- $line_count lines\n";
            print "- $char_count characters\n";
            print '*' x 60 . "\n\n";
            
            return 1;
        }
    };
    
    return undef;
}

# Execute main if called directly
main() unless caller;
