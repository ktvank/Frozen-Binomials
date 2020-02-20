#!/bin/bash
mkdir "all_words_lists_unfiltered"
for file in comments/*.json; do
	f=$(basename $file ".json")
	output="all_words_lists_unfiltered/${f}_all_lists.txt"
	cat $file| sed 's/[-;:",\.\?!\(\)]//g' | awk '{for (i = 2; i <= NF-1; ++i) {if ($i == "and" || $i == "or") {print $(i-1), $i, $(i+1)}}}' | sort -n > $output
done
file="posts.json"
f=$(basename $file ".json")
output="all_words_lists_unfiltered/${f}_all_lists.txt"
cat $file| sed 's/[-;:",\.\?!\(\)]//g' | awk '{for (i = 2; i <= NF-1; ++i) {if ($i == "and" || $i == "or") {print $(i-1), $i, $(i+1)}}}' | sort -n > $output