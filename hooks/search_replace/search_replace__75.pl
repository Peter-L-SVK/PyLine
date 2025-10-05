#!/usr/bin/env perl

# -----------------------------------------------------------------------
# Perl Search/Replace Hook for PyLine
# Description: Incremental search with line numbers, context, and highlighting
# Priority: 75
# Category: event_handlers
# Type: search_replace
# Copyright (C) 2025 Peter Leukanič
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
# -----------------------------------------------------------------------

use strict;
use warnings;
use JSON::PP;

# ANSI codes for highlight: blue background, white foreground
sub ansi_highlight {
    my ($text) = @_;
    return "\033[44m\033[97m$text\033[0m";
}

sub main {
    # Read JSON input context from STDIN
    my $json_input = do { local $/; <STDIN> };
    my $ctx = eval { JSON::PP->new->utf8->decode($json_input) };
    if (!$ctx || $@) {
        return {error => "Invalid JSON input", handled_output => 0};
    }

    my $search = $ctx->{search} // '';
    my $replace = defined $ctx->{replace} ? $ctx->{replace} : undef;
    my @lines = @{$ctx->{lines} // []};

    my $match_count = 0;
    my $replace_count = 0;

    # Detect whole word mode using special prefix
    my $whole_word = 0;
    my $actual_search = $search;
    
    if ($search =~ s/^\\b//) {
        $whole_word = 1;
        $actual_search = $search;
    }

    if (length($actual_search)) {
        if (defined $replace) {
            # REPLACE MODE: Return JSON for processing
            my @out;
            for my $i (0..$#lines) {
                my $line = $lines[$i];
                
                # Build the search pattern
                my $search_pattern;
                if ($whole_word) {
                    $search_pattern = qr/\b\Q$actual_search\E\b/;
                } else {
                    $search_pattern = qr/\Q$actual_search\E/;
                }
                
                # Count matches before replacement
                my $matches_in_line = () = $line =~ /$search_pattern/g;
                $match_count += $matches_in_line;
                
                # Perform replacement
                my $replacements = ($line =~ s/$search_pattern/$replace/g);
                $replace_count += $replacements;
                
                push @out, $line;
            }
            
            my $message;
            if ($whole_word) {
                $message = "$replace_count occurrences of whole word '$actual_search' replaced out of $match_count matches.";
            } else {
                $message = "$replace_count occurrences of '$actual_search' replaced out of $match_count matches.";
            }
            
            return {
                content => \@out,
                matches => $match_count,
                replaced => $replace_count,
                message => $message,
                handled_output => 1
            };
        } else {
            # SEARCH MODE: Output formatted text directly to STDOUT
            my @matching_lines;
            my $search_pattern;
            
            if ($whole_word) {
                $search_pattern = qr/\b\Q$actual_search\E\b/;
            } else {
                $search_pattern = qr/\Q$actual_search\E/;
            }
            
            # Find all matching lines first
            for (my $i = 0; $i < @lines; $i++) {
                my $line = $lines[$i];
                my $matches_in_line = () = $line =~ /$search_pattern/g;
                if ($matches_in_line > 0) {
                    push @matching_lines, {
                        line_num => $i + 1,
                        content => $line,
                        matches => $matches_in_line
                    };
                    $match_count += $matches_in_line;
                }
            }
            
            if (@matching_lines > 0) {
                if ($whole_word) {
                    print "Search results for whole word: $actual_search\n";
                } else {
                    print "Search results for: $actual_search\n";
                }
                print "=" x 80 . "\n";
                
                # Show matching lines with line numbers and highlighting
                foreach my $match (@matching_lines) {
                    my $line_num = $match->{line_num};
                    my $content = $match->{content};
                    my $matches_in_line = $match->{matches};
                    
                    # Highlight all occurrences in this line
                    $content =~ s/($search_pattern)/ansi_highlight($1)/ge;
                    
                    printf "Line %4d: %s\n", $line_num, $content;
                }
                
                print "=" x 80 . "\n";
                if ($whole_word) {
                    print "$match_count whole word matches for '$actual_search' found in " . scalar(@matching_lines) . " lines.\n";
                } else {
                    print "$match_count matches for '$actual_search' found in " . scalar(@matching_lines) . " lines.\n";
                }
            } else {
                if ($whole_word) {
                    print "No whole word matches found for: $actual_search\n";
                } else {
                    print "No matches found for: $actual_search\n";
                }
            }
            
            return {handled_output => 1};
        }
    } else {
        return {error => "Empty search pattern", handled_output => 0};
    }
}

my $result = main();

# Only output JSON if we're in replace mode or there's an error
my $search_mode = !defined $result->{content};

if ($search_mode && $result->{handled_output}) {
    exit 0;
} else {
    print JSON::PP->new->utf8->encode($result);
}
