package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"net/url"
	"os"
)

func main() {
	target := flag.String("url", "", "Target URL to crawl")
	maxPages := flag.Int("max-pages", 50, "Maximum pages to discover")
	output := flag.String("output", "bin/crawl-output.json", "JSON output path")
	flag.Parse()

	if *target == "" {
		fmt.Fprintln(os.Stderr, "missing --url")
		os.Exit(1)
	}

	parsed, err := url.Parse(*target)
	if err != nil {
		fmt.Fprintf(os.Stderr, "invalid URL: %v\n", err)
		os.Exit(1)
	}

	// Placeholder logic: seed the crawler from the target and return the home page.
	pages := []string{parsed.String()}
	if len(pages) > *maxPages {
		pages = pages[:*maxPages]
	}

	payload, err := json.MarshalIndent(pages, "", "  ")
	if err != nil {
		fmt.Fprintf(os.Stderr, "json marshal error: %v\n", err)
		os.Exit(1)
	}

	if err := os.WriteFile(*output, payload, 0o644); err != nil {
		fmt.Fprintf(os.Stderr, "write error: %v\n", err)
		os.Exit(1)
	}

	fmt.Fprintf(os.Stderr, "wrote %d discovered pages to %s\n", len(pages), *output)
}
