#!/usr/bin/env python3

# -----------------------------------------------------------------------
# Grammar Checker Hook for PyLine
# Description: Uses language_tool_python for advanced grammar checking with AI enhancements and uses external JSON configuration for flexibility
# Priority: 75
# Category: editing_ops
# Type: search_replace
# Copyright (C) 2025 Peter Leukanič
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
# -----------------------------------------------------------------------

import re
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
import numpy as np
import pandas as pd
from collections import Counter

LT_AVAILABLE = True
try:
    import language_tool_python
    from language_tool_python import Match
except ImportError:
    LT_AVAILABLE = False

    # Create a proper dummy Match class for type checking when language_tool_python is not available
    class Match:  # type: ignore[no-redef]
        def __init__(self) -> None:
            self.ruleId = ""
            self.category = ""
            self.message = ""
            self.replacements: List[str] = []
            self.offset = 0
            self.errorLength = 0


class ConfigManager:
    """Manages loading and accessing JSON configuration"""

    def __init__(self, config_path: Optional[str] = None) -> None:
        self.config_path = Path(config_path) if config_path else self.get_default_config_path()
        self.config = self.load_config()

    def get_default_config_path(self) -> Path:
        """Get path to grammar_config.json in same directory as hook"""
        hook_dir = Path(__file__).parent
        return hook_dir / "grammar_config.json"

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file with fallbacks"""
        default_config = self.get_default_config()

        try:
            if self.config_path.exists():
                with open(self.config_path, "r", encoding="utf-8") as f:
                    user_config = json.load(f)
                    # Deep merge with defaults
                    return self.merge_configs(default_config, user_config)
            else:
                # Create default config file
                self.create_default_config()
                return default_config
        except Exception as e:
            print(f"Config loading warning: {e}, using defaults")
            return default_config

    def get_default_config(self) -> Dict[str, Any]:
        """Return comprehensive default configuration"""
        return {
            "common_errors": {
                "their_there_theyre": [
                    {
                        "pattern": r"\btheir\b",
                        "suggestion": "they're",
                        "explanation": "their (possessive) vs they're (they are)",
                        "confidence": 0.7,
                    }
                ]
            },
            "writing_style_rules": {"sentence_length": {"too_long_threshold": 25, "too_short_threshold": 8}},
            "language_tool_config": {"disabled_rules": ["EN_QUOTES"]},
            "severity_levels": {"high": ["TYPOS"], "medium": ["GRAMMAR"]},
            "output_settings": {"show_statistics": True},
        }

    def merge_configs(self, default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge user config with defaults"""
        result = default.copy()

        for key, value in user.items():
            if isinstance(value, dict) and key in result and isinstance(result[key], dict):
                result[key] = self.merge_configs(result[key], value)
            else:
                result[key] = value

        return result

    def create_default_config(self) -> None:
        """Create default config file for user customization"""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.get_default_config(), f, indent=2)
            print(f"Created default config at: {self.config_path}")
        except Exception as e:
            print(f"Could not create config file: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get config value using dot notation"""
        keys = key.split(".")
        value = self.config

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default


class GrammarChecker:
    def __init__(self, config_path: Optional[str] = None) -> None:
        self.config = ConfigManager(config_path)

        # Statistical analysis for AI suggestions
        self.word_frequencies: Counter[str] = Counter()
        self.sentence_lengths: List[int] = []

    def load_technical_vocabulary(self) -> Set[str]:
        """Load technical terms from config to avoid false positives"""
        tech_vocab = set()

        # Load from config
        programming_terms = self.config.get("technical_vocabulary.programming_terms", [])
        cs_terms = self.config.get("technical_vocabulary.computer_science_terms", [])
        abbreviations = self.config.get("technical_vocabulary.common_abbreviations", [])

        tech_vocab.update(programming_terms)
        tech_vocab.update(cs_terms)
        tech_vocab.update(abbreviations)

        # Load case insensitive exceptions
        case_insensitive = self.config.get("spelling_exceptions.case_insensitive", [])
        tech_vocab.update(term.lower() for term in case_insensitive)

        return tech_vocab

    def should_exclude_line(self, line: str) -> bool:
        """Check if a line should be excluded from grammar checking"""
        exclude_patterns = self.config.get("content_filters.exclude_lines_matching", [])

        for pattern in exclude_patterns:
            if re.search(pattern, line):
                return True
        return False

    def filter_technical_content(self, text: str) -> str:
        """Filter out technical content before analysis"""
        lines = text.split("\n")
        filtered_lines = []

        for line in lines:
            if not self.should_exclude_line(line):
                filtered_lines.append(line)

        return "\n".join(filtered_lines)

    def check_grammar_with_tool(self, text: str) -> List["Match"]:
        """Use LanguageTool with proper context management"""
        if not LT_AVAILABLE:
            return []

        try:
            # Create tool instance for this specific check
            with language_tool_python.LanguageTool("en-US") as tool:
                # Apply disabled rules
                disabled_rules = self.config.get("language_tool_config.disabled_rules", [])
                if hasattr(tool, "disabled_rules"):
                    tool.disabled_rules.update(disabled_rules)

                # Perform the check
                matches: List["Match"] = tool.check(text)
                return matches
        except Exception as e:
            print(f"Grammar check error: {e}")
            return []

    def analyze_text_statistics(self, text: str) -> Dict[str, Any]:
        """Use pandas/numpy for text analysis using config thresholds"""
        sentences = re.split(r"[.!?]+", text)
        words = re.findall(r"\b\w+\b", text.lower())

        # Use pandas for analysis
        word_series = pd.Series(words)

        # Use numpy for numerical analysis
        sentence_lengths = [len(re.findall(r"\b\w+\b", s)) for s in sentences if s.strip()]
        avg_sentence_length = np.mean(sentence_lengths) if sentence_lengths else 0

        # Update frequencies for AI learning
        self.word_frequencies.update(words)
        self.sentence_lengths.extend(sentence_lengths)

        # Get thresholds from config
        vocab_threshold = self.config.get("writing_style_rules.vocabulary.diversity_threshold", 0.5)

        return {
            "word_count": len(words),
            "sentence_count": len([s for s in sentences if s.strip()]),
            "avg_sentence_length": round(avg_sentence_length, 2),
            "unique_words": len(set(words)),
            "vocabulary_diversity": len(set(words)) / max(1, len(words)),
            "most_common_words": word_series.value_counts().head(5).to_dict(),
            "readability_score": self.calculate_readability(text),
            "vocabulary_rich": (len(set(words)) / max(1, len(words))) > vocab_threshold,
        }

    def count_syllables(self, word: str) -> int:
        """Improved syllable count approximation with better handling of edge cases"""
        word = word.lower().strip()
        if not word or not word.isalpha():
            return 1  # Default for non-words or empty

        # Handle very short words
        if len(word) <= 2:
            return 1

        # Special cases
        if word.endswith("es") or word.endswith("ed"):
            if len(word) <= 4:
                return 1

        # Count vowel groups more accurately
        vowels = "aeiouy"
        count = 0
        prev_char_vowel = False

        for i, char in enumerate(word):
            is_vowel = char in vowels

            # Don't count 'y' as vowel at start of word
            if char == "y" and i == 0:
                is_vowel = False

            # Count vowel at start of vowel group
            if is_vowel and not prev_char_vowel:
                count += 1

            prev_char_vowel = is_vowel

        # Adjust for silent 'e' at end
        if word.endswith("e") and count > 1 and len(word) > 2:
            # But keep if preceded by 'l' and consonant before that (like "table")
            if not (word.endswith("le") and len(word) > 2 and word[-3] not in vowels):
                count -= 1

        # Ensure at least one syllable
        return max(1, count)

    def calculate_readability(self, text: str) -> float:
        """Calculate Flesch Reading Ease score with better error handling"""
        # Clean the text first
        text = re.sub(r"[^\w\s.!?]", " ", text)

        sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
        words = re.findall(r"\b\w+\b", text.lower())

        if not sentences or not words:
            return 60.0  # Default score for empty text

        # Filter out very short "sentences" that are probably headers
        sentences = [s for s in sentences if len(re.findall(r"\b\w+\b", s)) >= 3]

        if not sentences:
            return 60.0

        avg_sentence_length = len(words) / len(sentences)

        # Count syllables more reliably
        syllables = 0
        for word in words:
            syllables += self.count_syllables(word)

        avg_syllables_per_word = syllables / len(words)

        # Flesch Reading Ease formula
        try:
            score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
            return max(10.0, min(100.0, score))  # Reasonable bounds
        except (ValueError, ZeroDivisionError, TypeError):
            return 60.0  # Fallback score

    def check_grammar_advanced(self, text: str) -> List[Dict[str, Any]]:
        """Advanced grammar checking using config rules"""
        issues = []
        # Filter out technical content first
        filtered_text = self.filter_technical_content(text)

        # Load technical vocabulary for spell checking
        tech_vocab = self.load_technical_vocabulary()

        # 1. Use language_tool for comprehensive checking with context manager
        if LT_AVAILABLE:
            try:
                matches = self.check_grammar_with_tool(filtered_text)
                for match in matches:
                    # Skip spelling errors for technical terms
                    if self.is_technical_term(match, text, tech_vocab):
                        continue

                    severity = self.determine_severity(match.ruleId, match.category)
                    issues.append(
                        {
                            "type": "grammar",
                            "severity": severity,
                            "message": match.message,
                            "suggestion": match.replacements[0] if match.replacements else "",
                            "offset": match.offset,
                            "length": match.errorLength,
                            "category": match.category,
                            "rule": match.ruleId,
                        }
                    )
            except Exception as e:
                print(f"Advanced grammar check failed: {e}")

        # 2. Pattern-based checking from config with intelligent suggestions
        issues.extend(self.check_patterns_intelligent(filtered_text))

        # 3. Statistical analysis for writing style suggestions
        stats = self.analyze_text_statistics(filtered_text)
        issues.extend(self.analyze_writing_style(stats))

        return issues

    def is_technical_term(self, match: "Match", text: str, tech_vocab: Set[str]) -> bool:
        """Check if a match is actually a technical term"""
        if match.ruleId == "MORFOLOGIK_RULE_EN_US":
            matched_text = text[match.offset : match.offset + match.errorLength].lower()
            return matched_text in tech_vocab
        return False

    def determine_severity(self, rule_id: str, category: str) -> Any:
        """Determine severity based on config rules"""
        severity_config = self.config.get("severity_levels", {})

        for severity_level, rules in severity_config.items():
            if rule_id in rules or category in rules:
                return severity_level

        return "medium"  # Default

    def check_patterns_intelligent(self, text: str) -> List[Dict[str, Any]]:
        """Check for common error patterns with intelligent suggestions"""
        issues = []
        common_errors = self.config.get("common_errors", {})

        # Split text into lines to check exclusions
        lines = text.split("\n")
        current_pos = 0

        for line_num, line in enumerate(lines):
            if self.should_exclude_line(line):
                current_pos += len(line) + 1  # +1 for newline
                continue

            for error_type, patterns in common_errors.items():
                for pattern_config in patterns:
                    pattern = pattern_config["pattern"]
                    explanation = pattern_config["explanation"]
                    base_confidence = pattern_config.get("confidence", 0.7)

                    for match in re.finditer(pattern, line, re.IGNORECASE):
                        matched_text = match.group()

                        # Generate intelligent suggestion based on error type
                        suggestion = self.generate_intelligent_suggestion(
                            error_type, matched_text, match, pattern_config
                        )

                        if not suggestion or suggestion == matched_text:
                            continue  # Skip if no valid suggestion or no change needed

                        # Check context to reduce false positives
                        context = self.get_context(text, current_pos + match.start(), current_pos + match.end())
                        context_confidence = self.analyze_pattern_confidence(context, matched_text, pattern_config)

                        final_confidence = min(1.0, max(0.1, base_confidence + context_confidence))

                        issues.append(
                            {
                                "type": "common_error",
                                "severity": "medium",
                                "message": f"Possible error: {explanation}",
                                "suggestion": suggestion,
                                "offset": current_pos + match.start(),
                                "length": len(matched_text),
                                "category": error_type,
                                "base_confidence": base_confidence,
                                "final_confidence": final_confidence,
                            }
                        )

            current_pos += len(line) + 1  # +1 for newline

        return issues

    def analyze_context_complexity(self, text: str, issue: Dict[str, Any]) -> float:
        """AI: Analyze contextual complexity around issues"""
        context = self.get_context(text, issue["offset"], issue["offset"] + issue["length"], 100)

        # AI: Simple complexity heuristics
        words = re.findall(r"\b\w+\b", context)
        if not words:
            return 0.5

        # Complexity based on word diversity and sentence structure
        unique_ratio = len(set(words)) / len(words)
        long_words = sum(1 for w in words if len(w) > 6) / len(words)

        # AI: Combined complexity score
        complexity = (unique_ratio * 0.6) + (long_words * 0.4)
        return max(0.1, min(0.9, complexity))

    def calculate_ai_relevance(self, text: str, issue: Dict[str, Any]) -> float:
        """AI: Calculate how relevant this issue is for improvement"""
        # Factors: frequency, impact, ease of correction
        issue_text = text[issue["offset"] : issue["offset"] + issue["length"]].lower()
        frequency_weight = self.word_frequencies.get(issue_text, 1)
        impact_weight = {"high": 1.0, "medium": 0.7, "low": 0.4}.get(issue["severity"], 0.5)

        return (frequency_weight * impact_weight) / 10.0  # Normalized score

    def generate_intelligent_suggestion(
        self, error_type: str, matched_text: str, match: re.Match[str], pattern_config: Dict[str, Any]
    ) -> str:
        """Generate intelligent suggestions based on grammar rules"""

        if error_type == "missing_is":
            return self._fix_missing_is(matched_text, match)
        elif error_type == "missing_copula":
            return self._fix_missing_copula(matched_text, match)
        elif error_type == "greeting_missing_copula":
            return self._fix_missing_copula(matched_text, match)
        elif error_type == "question_structure":
            return self._fix_question_structure(matched_text, match)
        elif error_type == "sentence_endings":
            return self._fix_sentence_endings(matched_text, match)
        elif error_type == "statement_question_confusion":
            return self._fix_statement_question_confusion(matched_text, match)
        elif error_type == "comma_splices":
            return self._fix_comma_splices(matched_text, match)
        elif error_type == "subject_verb_agreement":
            return self._fix_subject_verb_agreement(matched_text, match)
        elif error_type == "their_there_theyre":
            return self._fix_their_there(matched_text, match)
        elif error_type == "your_youre":
            return self._fix_your_youre(matched_text, match)
        elif error_type == "its_its":
            return self._fix_its_its(matched_text, match)
        elif error_type == "then_than":
            return self._fix_then_than(matched_text, match)
        elif error_type == "missing_to":
            return self._fix_missing_to(matched_text, match)
        elif error_type == "missing_articles":
            return self._fix_missing_articles(matched_text, match)
        else:
            # Fallback to template-based suggestion
            suggestion_template = pattern_config.get("suggestion", "")
            if suggestion_template:
                try:
                    result = re.sub(pattern_config["pattern"], suggestion_template, matched_text, flags=re.IGNORECASE)
                    return str(result)  # Ensure we return a string
                except Exception:
                    return str(suggestion_template)  # Ensure we return a string
            return matched_text  # Return original if no suggestion

    def _fix_comma_splices(self, matched_text: str, match: re.Match[str]) -> str:
        """Fix comma splices with proper sentence separation"""
        groups = match.groups()
        if len(groups) >= 3:
            first_part = groups[0]
            subject = groups[1]
            verb_start = groups[2]
            return f"{first_part}. {subject} {verb_start}"
        return matched_text

    def _fix_missing_is(self, matched_text: str, match: re.Match[str]) -> str:
        """Intelligently fix missing 'is' with proper grammar"""
        groups = match.groups()
        if len(groups) >= 2:
            subject = groups[0]
            verb_part = groups[1]

            # Handle different subject types with proper verb agreement
            subject_lower = subject.lower()
            if subject_lower == "i":
                return f"{subject} am {verb_part}"
            elif subject_lower in ["he", "she", "it", "that", "this"]:
                return f"{subject} is {verb_part}"
            elif subject_lower in ["you", "we", "they", "there"]:
                return f"{subject} are {verb_part}"
            else:
                # Default to 'is' for unknown subjects
                return f"{subject} is {verb_part}"

        return matched_text

    def _fix_missing_copula(self, matched_text: str, match: re.Match[str]) -> str:
        """Fix missing copula verbs with advanced context detection"""
        try:
            groups = match.groups()
            if not groups or len(groups) < 3:
                return matched_text

            greeting, pronoun, rest = groups[0], groups[1], groups[2]

            # Better question detection
            is_question = matched_text.strip().endswith("?") or any(
                rest.lower().startswith(q_word)
                for q_word in ["who", "what", "where", "when", "why", "how", "which", "whose"]
            )

            # Determine correct verb
            if pronoun.lower() in ["this", "that", "it"]:
                copula = "is"
            elif pronoun.lower() in ["these", "those", "they"]:
                copula = "are"
            else:
                copula = "is"

            if is_question:
                # Questions: invert structure and add comma after greeting
                clean_rest = rest.rstrip("? ").strip()
                return f"{greeting}, {copula} {pronoun} {clean_rest}?"
            else:
                # Statements: keep direct structure
                return f"{greeting} {pronoun} {copula} {rest}"

        except Exception as e:
            print(f"Error in _fix_missing_copula: {e}")

        return matched_text

    def _fix_subject_verb_agreement(self, matched_text: str, match: re.Match[str]) -> str:
        """Fix subject-verb agreement errors"""
        groups = match.groups()
        if len(groups) >= 2:
            subject = groups[0]
            wrong_verb = groups[1]

            subject_lower = subject.lower()
            if subject_lower in ["i", "you", "we", "they"]:
                if wrong_verb == "is":
                    return f"{subject} are"
                elif wrong_verb == "was":
                    return f"{subject} were"
            elif subject_lower in ["he", "she", "it"]:
                if wrong_verb == "are":
                    return f"{subject} is"
                elif wrong_verb == "were":
                    return f"{subject} was"

        return matched_text

    def _fix_question_structure(self, matched_text: str, match: re.Match[str]) -> str:
        """Fix question structure issues"""
        # Capitalize questions that don't start with capital
        if matched_text and matched_text[0].islower() and matched_text.endswith("?"):
            return matched_text[0].upper() + matched_text[1:]

        # Add question mark to questions
        if not matched_text.endswith("?"):
            if matched_text.lower().startswith(
                (
                    "is ",
                    "are ",
                    "am ",
                    "was ",
                    "were ",
                    "do ",
                    "does ",
                    "did ",
                    "have ",
                    "has ",
                    "had ",
                    "can ",
                    "could ",
                    "will ",
                    "would ",
                    "should ",
                    "may ",
                    "might ",
                    "must ",
                    "why ",
                    "what ",
                    "when ",
                    "where ",
                    "who ",
                    "how ",
                    "which ",
                    "whose ",
                )
            ):
                return matched_text + "?"

        return matched_text

    def _fix_sentence_endings(self, matched_text: str, match: re.Match[str]) -> str:
        """Fix sentence ending punctuation"""
        # Add period to declarative sentences
        if not matched_text.endswith((".", "!", "?")):
            if matched_text.lower().startswith(("this is ", "that is ", "it is ", "there is ", "here is ")):
                return matched_text + "."
            elif matched_text and matched_text[0].isupper():
                return matched_text + "."

        # Capitalize after sentence endings
        if re.search(r"[.!?]\s+[a-z]", matched_text):
            result = re.sub(r"([.!?]\s+)([a-z])", lambda m: m.group(1) + m.group(2).upper(), matched_text)
            return str(result)  # Ensure we return a string

        return matched_text

    def _fix_statement_question_confusion(self, matched_text: str, match: re.Match[str]) -> str:
        """Fix confusion between statements and questions"""
        # Statement with question mark -> remove question mark
        if matched_text.endswith("?") and matched_text.lower().startswith(("this is ", "that is ", "it is ")):
            return matched_text[:-1] + "."

        # Question without question mark -> add question mark
        if not matched_text.endswith("?") and matched_text.lower().startswith(
            (
                "is ",
                "are ",
                "am ",
                "was ",
                "were ",
                "do ",
                "does ",
                "did ",
                "have ",
                "has ",
                "had ",
                "can ",
                "could ",
                "will ",
                "would ",
                "should ",
                "may ",
                "might ",
                "must ",
            )
        ):
            return matched_text + "?"

        return matched_text

    def _fix_their_there(self, matched_text: str, match: re.Match[str]) -> str:
        """Fix their/there/they're confusion"""
        # Simple replacement - in a real system you'd analyze context
        if matched_text.lower() == "their":
            return "they're"
        elif matched_text.lower() == "there":
            return "they're"
        return matched_text

    def _fix_your_youre(self, matched_text: str, match: re.Match[str]) -> str:
        """Fix your/you're confusion"""
        if matched_text.lower() == "your":
            return "you're"
        return matched_text

    def _fix_its_its(self, matched_text: str, match: re.Match[str]) -> str:
        """Fix its/it's confusion"""
        if matched_text.lower() == "its":
            return "it's"
        return matched_text

    def _fix_then_than(self, matched_text: str, match: re.Match[str]) -> str:
        """Fix then/than confusion"""
        if matched_text.lower() == "then":
            return "than"
        return matched_text

    def _fix_missing_to(self, matched_text: str, match: re.Match[str]) -> str:
        """Add missing 'to' before verbs"""
        groups = match.groups()
        if len(groups) >= 2:
            verb = groups[0]
            main_verb = groups[1]
            return f"{verb} to {main_verb}"
        return matched_text

    def _fix_missing_articles(self, matched_text: str, match: re.Match[str]) -> str:
        """Fix missing articles"""
        groups = match.groups()
        if len(groups) >= 3:
            subject = groups[0]
            verb = groups[1]
            noun = groups[2]

            # Determine if we need 'a' or 'an'
            if noun[0].lower() in "aeiou":
                return f"{subject} {verb} an {noun}"
            else:
                return f"{subject} {verb} a {noun}"

        return matched_text

    def find_line_number(self, content: List[str], offset: int) -> int:
        """Find the line number for a given character offset"""
        current_pos = 0
        for line_num, line in enumerate(content, 1):
            line_length = len(line) + 1  # +1 for newline character
            if current_pos <= offset < current_pos + line_length:
                return line_num
            current_pos += line_length
        return 1  # Default to line 1 if not found

    def analyze_pattern_confidence(self, context: str, matched_text: str, pattern_config: Dict[str, Any]) -> float:
        """Analyze context to adjust confidence for pattern matches"""
        context_rules = pattern_config.get("context_rules", {})
        confidence_factors = self.config.get("confidence_factors", {})

        confidence_adjustment = 0

        # Check for likely correct usage
        likely_correct = context_rules.get("likely_correct")
        if likely_correct and re.search(likely_correct, context, re.IGNORECASE):
            confidence_adjustment += confidence_factors.get("context_boost", 0.1)

        # Check for likely incorrect usage
        likely_incorrect = context_rules.get("likely_incorrect")
        if likely_incorrect and re.search(likely_incorrect, context, re.IGNORECASE):
            confidence_adjustment += confidence_factors.get("context_penalty", -0.2)

        return confidence_adjustment

    def get_context(self, text: str, start: int, end: int, context_size: int = 50) -> str:
        """Get context around a match for better analysis"""
        context_start = max(0, start - context_size)
        context_end = min(len(text), end + context_size)
        return text[context_start:context_end]

    def analyze_writing_style(self, stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Provide AI-powered writing suggestions using config thresholds"""
        suggestions = []
        style_rules = self.config.get("writing_style_rules", {})

        # Sentence length analysis
        length_rules = style_rules.get("sentence_length", {})
        avg_length = stats["avg_sentence_length"]

        too_long = length_rules.get("too_long_threshold", 25)
        too_short = length_rules.get("too_short_threshold", 8)

        if avg_length > too_long:
            suggestions.append(
                {
                    "type": "style",
                    "severity": "low",
                    "message": f"Average sentence length ({avg_length}) is quite long",
                    "suggestion": f"Consider breaking up sentences longer than {too_long} words",
                    "offset": 0,
                    "length": 0,
                    "category": "sentence_length",
                }
            )
        elif avg_length < too_short:
            suggestions.append(
                {
                    "type": "style",
                    "severity": "low",
                    "message": f"Short sentences (avg: {avg_length} words) can feel choppy",
                    "suggestion": "Vary sentence length for better flow",
                    "offset": 0,
                    "length": 0,
                    "category": "sentence_variety",
                }
            )

        # Readability suggestions
        readability_rules = style_rules.get("readability", {})
        readability = stats["readability_score"]

        excellent = readability_rules.get("excellent_threshold", 80)
        good = readability_rules.get("good_threshold", 60)

        if readability < good:
            suggestions.append(
                {
                    "type": "readability",
                    "severity": "medium",
                    "message": f"Readability score: {readability:.1f}/100",
                    "suggestion": "Use shorter words and sentences to improve readability",
                    "offset": 0,
                    "length": 0,
                    "category": "readability",
                }
            )
        elif readability < excellent:
            suggestions.append(
                {
                    "type": "readability",
                    "severity": "low",
                    "message": f"Readability score: {readability:.1f}/100 - Good",
                    "suggestion": "Your writing is clear and accessible",
                    "offset": 0,
                    "length": 0,
                    "category": "readability",
                }
            )

        return suggestions

    def get_enhanced_suggestions(self, text: str, original_issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Use numpy/pandas for advanced AI analysis"""
        if not original_issues:
            return []

        # Convert to pandas DataFrame for AI analysis
        df = pd.DataFrame(original_issues)

        if df.empty:
            return []

        # AI: Analyze issue patterns
        temporal_patterns = df.groupby("category").size().sort_values(ascending=False)

        # AI: Use numpy for advanced confidence scoring
        base_confidences = np.array([issue.get("base_confidence", 0.5) for issue in original_issues])
        context_factors = np.array([self.analyze_context_complexity(text, issue) for issue in original_issues])

        # AI: Machine learning-style weighted confidence
        final_confidences = 0.6 * base_confidences + 0.4 * context_factors

        enhanced_issues = []

        # AI: Add pattern insights
        if len(original_issues) > 5:
            common_pattern = temporal_patterns.index[0]
            enhanced_issues.append(
                {
                    "type": "ai_insight",
                    "severity": "info",
                    "message": f"AI detected frequent {common_pattern} patterns in your writing",
                    "suggestion": f"Focus on improving {common_pattern} for better clarity",
                    "offset": 0,
                    "length": 0,
                    "category": "ai_analysis",
                    "confidence": 0.85,
                }
            )

        # Enhance original issues with AI confidence scores
        for i, issue in enumerate(original_issues[:15]):  # AI: Limit based on importance
            enhanced_issue = issue.copy()
            enhanced_issue["confidence"] = round(final_confidences[i], 2)
            enhanced_issue["ai_score"] = self.calculate_ai_relevance(text, issue)
            enhanced_issues.append(enhanced_issue)

        return enhanced_issues


def main(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main hook function for grammar checking
    Now with configurable JSON settings
    """
    grammar_checker = None
    try:
        # Allow custom config path via context
        config_path = context.get("grammar_config_path")
        grammar_checker = GrammarChecker(config_path)

        if context.get("action") != "process_content":
            return {"handled_output": 0}

        content = context.get("content", [])
        if not content:
            return {"handled_output": 0}

        # Convert lines to single text for analysis
        full_text = "\n".join(content)

        # Perform grammar check
        issues = grammar_checker.check_grammar_advanced(full_text)

        # Map issues to line numbers
        line_issues = []
        for issue in issues:
            line_num = grammar_checker.find_line_number(content, issue["offset"])
            issue["line"] = line_num
            line_issues.append(issue)

        enhanced_issues = grammar_checker.get_enhanced_suggestions(full_text, line_issues)

        # Get text statistics
        stats = grammar_checker.analyze_text_statistics(full_text)

        # Prepare output based on config
        output_settings = grammar_checker.config.get("output_settings", {})
        output_lines = []

        if output_settings.get("show_statistics", True):
            output_lines.append("=" * 60)
            output_lines.append("PYLINE GRAMMAR CHECKER - AI ENHANCED")
            output_lines.append("=" * 60)
            output_lines.append("")
            output_lines.append("📊 TEXT STATISTICS:")
            output_lines.append(f"  Words: {stats['word_count']}")
            output_lines.append(f"  Sentences: {stats['sentence_count']}")
            output_lines.append(f"  Avg. Sentence Length: {stats['avg_sentence_length']} words")
            output_lines.append(f"  Vocabulary Diversity: {stats['vocabulary_diversity']:.1%}")
            output_lines.append(f"  Readability Score: {stats['readability_score']:.1f}/100")
            output_lines.append("")

        # Show issues
        if enhanced_issues:
            output_lines.append("🔍 GRAMMAR & STYLE ISSUES:")

            # Group by category or severity based on config
            group_by = "category"
            if output_settings.get("group_by_severity"):
                group_by = "severity"

            by_group: Dict[str, List[Dict[str, Any]]] = {}
            for issue in enhanced_issues:
                group = issue.get(group_by, "other")
                if group not in by_group:
                    by_group[group] = []
                by_group[group].append(issue)

            for group, group_issues in by_group.items():
                output_lines.append(f"  {group.upper()}:")
                for issue in group_issues:
                    severity_icon = {"high": "❌", "medium": "⚠️", "low": "💡", "info": "ℹ️"}.get(issue["severity"], "•")

                    confidence_display = ""
                    if output_settings.get("show_confidence_scores") and "confidence" in issue:
                        confidence_display = f"({issue['confidence'] * 100:.0f}% confidence)"

                    line_display = f"Line {issue['line']}: " if issue.get("line") else ""
                    output_lines.append(
                        f"    {severity_icon} {line_display}{issue['message']} {confidence_display}".strip()
                    )
                    if issue.get("suggestion"):
                        output_lines.append(f"      💡 Suggestion: {issue['suggestion']}")
                output_lines.append("")
        else:
            output_lines.append("✅ No grammar issues found! Your writing looks good.")
            output_lines.append("")

        # Writing tips
        if output_settings.get("show_writing_tips", True):
            output_lines.append("📝 WRITING TIPS:")

            if stats["readability_score"] < 60:
                output_lines.append("  • Consider using shorter sentences for better readability")
            if not stats["vocabulary_rich"]:
                output_lines.append("  • Try varying your vocabulary for more engaging writing")
            if 10 <= stats["avg_sentence_length"] <= 20:
                output_lines.append("  • Good sentence length variation detected!")

            output_lines.append("")
            output_lines.append("💡 Tip: Run this check after writing to catch common errors.")

        output_lines.append("=" * 60)

        return {"handled_output": 1, "output": "\n".join(output_lines)}

    except Exception as e:
        return {
            "handled_output": 1,
            "output": f"Grammar check error: {str(e)}\nInstall: pip install language-tool-python numpy pandas",
        }


# For testing the hook directly
if __name__ == "__main__":
    test_context = {
        "action": "process_content",
        "content": [
            "This is an test sentence with some error.",
            "Their going to the park and there having fun.",
            "Your welcome to join us whenever your ready.",
            "Its a beautiful day outside.",
        ],
        "filename": "test.txt",
    }

    result = main(test_context)
    print(result.get("output", ""))
