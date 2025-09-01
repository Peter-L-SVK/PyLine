#!/usr/bin/env perl

#-----------------------------------------------------------------------
# Perl Lower-case to Upper-case Hook
# Description: Converts all lower-case letters to upper-case in opened files
# Priority: 80
# Copyright (C) 2025 Peter Leukanič
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
#-----------------------------------------------------------------------

use strict;
use warnings;

sub main {
    # Read all input from STDIN
    my $json_input = do { local $/; <STDIN> };

    # Parse the JSON input
    my $data;
    eval {
        require JSON;
        $data = JSON::decode_json($json_input);
    };

    if ($@) {
        # Invalid JSON, exit with error
        exit 1;
    }

    # Check if this is a pre_load event
    if ($data->{action} && $data->{action} eq 'pre_load') {
        my $filename = $data->{filename};
        my $content = '';
    
        # If content is provided in the JSON, use it
        if (exists $data->{content}) {
            $content = $data->{content};
        } 
        # Otherwise, read the file ourselves
        elsif ($filename && -f $filename) {
            open(my $fh, '<:encoding(UTF-8)', $filename) or exit 1;
            local $/;
            $content = <$fh>;
            close($fh);
        } else {
            exit 1;  # No filename or file doesn't exist
        }
    
        # Convert all lowercase letters to uppercase
        $content = uc($content);
    
        # RETURN JUST THE TRANSFORMED CONTENT (not JSON)
        print $content;
        exit 0;
    }

    # If not pre_load, exit with error
    exit 1;
};

main() unless caller;
