#!/usr/bin/env python3

# -----------------------------------------------------------------------
# Grammar Checker Hook for PyLine
# Description: Grammar + spell checking using LanguageTool, pyspellchecker, textstat
# Priority: 75
# Category: editing_ops
# Type: search_replace
# Copyright (C) 2025 Peter Leukanič
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# -----------------------------------------------------------------------

import re
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple
import textstat

# Optional dependencies
LT_AVAILABLE = True
try:
    import language_tool_python
except ImportError:
    LT_AVAILABLE = False

SPELLCHECK_AVAILABLE = True
try:
    from spellchecker import SpellChecker
except ImportError:
    SPELLCHECK_AVAILABLE = False


class ConfigManager:
    """Manages loading and accessing JSON configuration"""
    
    def __init__(self, config_path: Optional[str] = None) -> None:
        self.config_path = Path(config_path) if config_path else Path(__file__).parent / "grammar_config.json"
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        try:
            if self.config_path.exists():
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            print(f"Config not found at {self.config_path}, using defaults")
            return {}
        except Exception as e:
            print(f"Config loading error: {e}")
            return {}
    
    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split(".")
        value = self.config
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default


class SpellCheckerWrapper:
    """Wrapper around pyspellchecker with config integration"""
    
    def __init__(self, config: ConfigManager):
        self.enabled = config.get("spellcheck.enabled", True)
        
        if self.enabled and SPELLCHECK_AVAILABLE:
            self.spell = SpellChecker()
            
            self.max_suggestions = config.get("spellcheck.max_suggestions", 3)
            self.distance = config.get("spellcheck.distance", 2)
            self.ignore_patterns = config.get("spellcheck.ignore_patterns", [])
            
            if hasattr(self.spell, 'distance'):
                self.spell.distance = self.distance
            
            custom_words = set()
            custom_words.update(config.get("spellcheck.ignore_words", []))
            custom_words.update(config.get("technical_vocabulary", []))
            
            if custom_words:
                self.spell.word_frequency.load_words(list(custom_words))
        else:
            self.spell = None
    
    def should_ignore_word(self, word: str) -> bool:
        for pattern in self.ignore_patterns:
            if re.match(pattern, word):
                return True
        return False
    
    def check_word(self, word: str) -> Optional[Dict[str, Any]]:
        if not self.spell or not self.enabled:
            return None
        if self.should_ignore_word(word):
            return None
        if not word.isalpha():
            return None
        if len(word) < 3:
            return None
        
        if word not in self.spell:
            correction = self.spell.correction(word)
            candidates = self.spell.candidates(word)
            if correction and correction != word:
                return {
                    "word": word,
                    "correction": correction,
                    "candidates": list(candidates)[:self.max_suggestions]
                }
        return None
    
    def check_text(self, text: str, skip_words: Set[str] = None) -> List[Dict[str, Any]]:
        if not self.spell or not self.enabled:
            return []
        if skip_words is None:
            skip_words = set()
        
        issues = []
        for match in re.finditer(r'\b\w+\b', text):
            word = match.group()
            if word.lower() in skip_words:
                continue
            result = self.check_word(word)
            if result:
                result["offset"] = match.start()
                result["length"] = match.end() - match.start()
                issues.append(result)
        return issues


class GrammarChecker:
    """Grammar checker using LanguageTool and pyspellchecker"""
    
    def __init__(self, config_path: Optional[str] = None) -> None:
        self.config = ConfigManager(config_path)
        self.tool = None
        
        if LT_AVAILABLE:
            try:
                language = self.config.get("language_tool.language", "en-US")
                self.tool = language_tool_python.LanguageTool(language)
                disabled_rules = self.config.get("language_tool.disabled_rules", [])
                if hasattr(self.tool, 'disabled_rules'):
                    self.tool.disabled_rules.update(disabled_rules)
            except Exception as e:
                print(f"Failed to initialize LanguageTool: {e}")
                self.tool = None
        
        self.spell_checker = SpellCheckerWrapper(self.config)
        self.tech_vocab = set(word.lower() for word in self.config.get("technical_vocabulary", []))
    
    def _clean_context(self, text: str, matched_word: str = "") -> str:
        """Clean up context text for display"""
        # Replace newlines with spaces
        text = text.replace('\n', ' ').strip()
        # Collapse multiple spaces
        text = re.sub(r'\s+', ' ', text)
        # Highlight the error word if provided
        if matched_word and matched_word in text:
            text = text.replace(matched_word, f"**{matched_word}**", 1)
        return text
    
    def find_line_number(self, text: str, offset: int) -> int:
        lines = text[:offset].split('\n')
        return len(lines)
    
    def filter_technical_content(self, text: str) -> str:
        exclude_lines = self.config.get("content_filters.exclude_lines_matching", [])
        lines = text.split("\n")
        filtered_lines = []
        for line in lines:
            should_exclude = any(re.search(pattern, line) for pattern in exclude_lines)
            if not should_exclude:
                filtered_lines.append(line)
        return "\n".join(filtered_lines)
    
    def check_grammar(self, text: str) -> Tuple[List[Dict[str, Any]], Set[str]]:
        if not self.tool:
            return [], set()

        filtered_text = self.filter_technical_content(text)
        words_flagged = set()

        try:
            matches = self.tool.check(filtered_text)
            issues = []

            for match in matches:
                rule_id = getattr(match, 'ruleId', None) or getattr(match, 'rule_id', 'UNKNOWN')
                category = getattr(match, 'category', 'UNKNOWN')
                offset = getattr(match, 'offset', 0)
                error_length = getattr(match, 'errorLength', None) or getattr(match, 'error_length', 0)
                replacements = getattr(match, 'replacements', [])
                message = getattr(match, 'message', '')
                
                matched_word = ""
                if offset < len(filtered_text) and error_length > 0:
                    matched_word = filtered_text[offset:offset + error_length]
                
                if "MORFOLOGIK" in rule_id and matched_word.lower() in self.tech_vocab:
                    continue
                
                if matched_word:
                    words_flagged.add(matched_word.lower())
                
                is_spelling = "MORFOLOGIK" in rule_id or "spelling" in category.lower()
                issue_type = "spelling" if is_spelling else "grammar"
                
                if is_spelling and matched_word:
                    suggestion = replacements[0] if replacements else ""
                    if "Possible spelling mistake" in message:
                        message = f"Spelling: '{matched_word}' → '{suggestion}'"
                
                line_num = self.find_line_number(filtered_text, offset)
                context_start = max(0, offset - 40)
                context_end = min(len(filtered_text), offset + error_length + 40)
                context = filtered_text[context_start:context_end]
                context = self._clean_context(context, matched_word)
                
                issue = {
                    "type": issue_type,
                    "message": message,
                    "suggestion": replacements[0] if replacements else "",
                    "offset": offset,
                    "length": error_length,
                    "category": category,
                    "rule": rule_id,
                    "matched_word": matched_word,
                    "line": line_num,
                    "context": context
                }
                issues.append(issue)
        
            return issues[:self.config.get("output_settings.max_issues", 30)], words_flagged

        except Exception as e:
            print(f"Grammar check error: {e}")
            return [], set()
    
    def check_spelling(self, text: str, words_to_skip: Set[str] = None) -> List[Dict[str, Any]]:
        if not self.config.get("output_settings.show_spelling", True):
            return []
        if words_to_skip is None:
            words_to_skip = set()
        
        filtered_text = self.filter_technical_content(text)
        spelling_issues = self.spell_checker.check_text(filtered_text, words_to_skip)
        
        issues = []
        for issue in spelling_issues:
            line_num = self.find_line_number(filtered_text, issue['offset'])
            context_start = max(0, issue['offset'] - 40)
            context_end = min(len(filtered_text), issue['offset'] + issue['length'] + 40)
            context = filtered_text[context_start:context_end]
            context = self._clean_context(context, issue['word'])
            
            issues.append({
                "type": "spelling",
                "message": f"Misspelled word: '{issue['word']}'",
                "suggestion": issue['correction'],
                "options": issue.get('candidates', []),
                "offset": issue['offset'],
                "length": issue['length'],
                "category": "SPELLING",
                "rule": "SPELL_CHECK",
                "line": line_num,
                "context": context
            })
        return issues
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        try:
            return {
                "word_count": textstat.lexicon_count(text, removepunct=True),
                "sentence_count": textstat.sentence_count(text),
                "avg_sentence_length": textstat.words_per_sentence(text),
                "flesch_reading_ease": textstat.flesch_reading_ease(text),
                "flesch_kincaid_grade": textstat.flesch_kincaid_grade(text),
                "gunning_fog": textstat.gunning_fog(text),
                "difficult_words": textstat.difficult_words(text)
            }
        except Exception as e:
            print(f"Text analysis error: {e}")
            return {}
    
    def get_writing_tips(self, stats: Dict[str, Any]) -> List[str]:
        tips = []
        readability = stats.get("flesch_reading_ease", 100)
        threshold = self.config.get("writing_tips.readability_threshold", 60)
        
        if readability < threshold:
            tips.append(f"Readability score is {readability:.0f}/100. Consider shorter sentences and simpler words.")
        elif readability >= 80:
            tips.append(f"Excellent readability score: {readability:.0f}/100!")
        
        avg_length = stats.get("avg_sentence_length", 0)
        ideal_range = self.config.get("writing_tips.sentence_length_ideal", [15, 20])
        
        if 0 < avg_length < ideal_range[0]:
            tips.append(f"Average sentence length ({avg_length:.1f}) is short. Consider combining some sentences.")
        elif avg_length > ideal_range[1]:
            tips.append(f"Average sentence length ({avg_length:.1f}) is long. Consider breaking up long sentences.")
        
        return tips
    
    def close(self):
        if self.tool:
            try:
                self.tool.close()
            except:
                pass


def main(context: Dict[str, Any]) -> Dict[str, Any]:
    checker = None
    try:
        config_path = context.get("grammar_config_path")
        checker = GrammarChecker(config_path)
        
        if context.get("action") != "process_content":
            return {"handled_output": 0}
        
        content = context.get("content", [])
        if not content:
            return {"handled_output": 0}
        
        full_text = "\n".join(content)
        
        grammar_issues, words_flagged = checker.check_grammar(full_text)
        spelling_issues = checker.check_spelling(full_text, words_flagged)
        all_issues = grammar_issues + spelling_issues
        all_issues.sort(key=lambda x: x.get('line', 0))
        
        stats = {}
        if checker.config.get("output_settings.show_statistics", True):
            stats = checker.analyze_text(full_text)
        
        output_lines = []
        output_lines.append("=" * 60)
        output_lines.append("PYLINE GRAMMAR & SPELL CHECKER")
        output_lines.append("=" * 60)
        output_lines.append("")
        
        if stats and checker.config.get("output_settings.show_statistics", True):
            output_lines.append("📊 TEXT STATISTICS:")
            output_lines.append(f"  Words: {stats.get('word_count', 0)}")
            output_lines.append(f"  Sentences: {stats.get('sentence_count', 0)}")
            output_lines.append(f"  Avg. Sentence Length: {stats.get('avg_sentence_length', 0):.1f} words")
            output_lines.append(f"  Readability (Flesch): {stats.get('flesch_reading_ease', 0):.1f}/100")
            output_lines.append(f"  Grade Level: {stats.get('flesch_kincaid_grade', 0):.1f}")
            output_lines.append("")
        
        if all_issues:
            grammar = [i for i in all_issues if i['type'] == 'grammar']
            spelling_lt = [i for i in all_issues if i['type'] == 'spelling' and i.get('rule', '') != 'SPELL_CHECK']
            spelling_ps = [i for i in all_issues if i['type'] == 'spelling' and i.get('rule', '') == 'SPELL_CHECK']
            
            output_lines.append(f"🔍 ISSUES FOUND: {len(all_issues)} total ({len(grammar)} grammar + {len(spelling_lt) + len(spelling_ps)} spelling)")
            output_lines.append("")
            
            if grammar:
                output_lines.append("📝 GRAMMAR ISSUES:")
                for issue in sorted(grammar, key=lambda x: x.get('line', 0)):
                    line_num = issue.get('line', '?')
                    context = issue.get('context', '')
                    output_lines.append(f"  Line {line_num}: {issue['message']}")
                    if context:
                        output_lines.append(f"    📍 \"...{context}...\"")
                    if issue.get('suggestion'):
                        output_lines.append(f"    💡 {issue['suggestion']}")
                output_lines.append("")
            
            if spelling_lt or spelling_ps:
                output_lines.append("🔤 SPELLING ISSUES:")
                for issue in sorted(spelling_lt + spelling_ps, key=lambda x: x.get('line', 0)):
                    line_num = issue.get('line', '?')
                    context = issue.get('context', '')
                    output_lines.append(f"  Line {line_num}: {issue['message']}")
                    if context:
                        output_lines.append(f"    📍 \"...{context}...\"")
                    if issue.get('suggestion'):
                        output_lines.append(f"    💡 {issue['suggestion']}")
                output_lines.append("")
        else:
            output_lines.append("✅ No issues found!")
            output_lines.append("")
        
        if stats and checker.config.get("output_settings.show_writing_tips", True):
            tips = checker.get_writing_tips(stats)
            if tips:
                output_lines.append("📝 WRITING TIPS:")
                for tip in tips:
                    output_lines.append(f"  • {tip}")
                output_lines.append("")
        
        output_lines.append("=" * 60)
        
        return {"handled_output": 1, "output": "\n".join(output_lines)}
    
    except Exception as e:
        return {
            "handled_output": 1,
            "output": f"Grammar check error: {str(e)}\n\nRequired: pip install language-tool-python textstat pyspellchecker"
        }
    
    finally:
        if checker:
            checker.close()


if __name__ == "__main__":
    test_context = {
        "action": "process_content",
        "content": [
            "The Wonderful World of Berry Fruits",
            "",
            "Their are many different types of berry fruits in the world. My favorite type of bery is the strawberry, which are actually not a true berry but a aggregate fruit. Its interesting to learn about how berrys grow and their nutritional benefits.",
            "",
            "Many people don't know that bananas is technically a bery, while strawberries is not. This always surprise people when I tell them about it. The definition of a true berry is a fruit that develop from a single ovary and has seeds inside the flesh.",
            "",
            "Eating berrys is very good for you're health. They contain many antioxidants which help protect the body. Blueberries, raspberries, and blackberries is all excellent sources of vitamins. My grandmother always said \"an apple a day keeps the doctor away,\" but I think berrys should get more recognition for there health benefits.",
            "",
            "Yesterday I went to the farm to pick fresh berrys with my family. We're baskets was full by the end of the day. The farmer told us that berry season are usually in the summer months. I love the taste of fresh, ripe berrys more then anything else.",
            "",
            "In conclusion, berry fruits is fascinating and delicious. Weather you prefer strawberries, blueberries, or raspberries, there all wonderful additions to a healthy diet. I think everyone should try growing there own berry plants at home."
        ],
        "filename": "berry_essay.txt"
    }
    
    result = main(test_context)
    print(result.get("output", ""))
