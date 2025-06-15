#!/usr/bin/env python3
import argparse
import random
import os
from typing import List, Tuple

def generate_random_url() -> str:
    """Generate a random URL."""
    tlds = [
        "com", "org", "net", "io", "dev", "site", "app", "co", "info", "biz",
        "tech", "online", "store", "blog", "cloud", "digital", "network", "systems", "media", "solutions",
        "xyz", "ai", "edu", "gov", "pro"
    ]

    domains = [
        "example", "test", "sample", "demo", "mock", "fake", "dummy", "techblog", "codehub",
        "datastore", "cloudapp", "webservice", "apphosting", "devzone", "codebase", "sitebuild",
        "webportal", "appstack", "hostingpro", "serverless", "cloudstack", "webtools", "appfactory",
        "codeforge", "datasync", "netportal", "devhub", "cloudstore", "appmarket", "codelab",
        "webcloud", "techspot", "codemaster", "webexpert", "appworld", "datasphere", "netcraft",
        "cloudmaster", "devcraft", "techzone", "appuniverse", "webmatrix", "dataflow", "netstream",
        "cloudpulse", "devpulse", "techforge", "appnexus", "webforge", "datacraft",
        "techbridge", "datahub", "codestream", "appcloud", "webstack", "netforge", "cloudzone",
        "devstore", "techflow", "appcraft", "webpulse", "datamatrix", "netcloud", "codeportal", "devapp"
    ]

    subdomains = [
        "www", "api", "blog", "shop", "app", "mail", "dev", "test", "admin", "",
        "docs", "support", "help", "store", "cdn", "static", "media", "images", "videos", "files",
        "auth", "login", "account", "dashboard", "portal", "secure", "beta", "staging", "prod", "production",
        "internal", "external", "public", "private", "corporate", "enterprise", "mobile", "desktop", "web", "cloud",
        "forum", "community", "status", "analytics", "data", "tools", "services", "apps", "download", "upload",
        "connect", "chat", "live", "stream", "events"
    ]

    # Pick 3 domain parts and 1 TLD
    domain_parts = random.sample(domains, 3)
    tld = random.choice(tlds)

    # Combine domain parts with hyphens and add TLD
    domain = f"{'-'.join(domain_parts)}.{tld}"

    subdomain = random.choice(subdomains)

    if subdomain:
        return f"{subdomain}.{domain}"
    else:
        return domain

def generate_random_category_name() -> str:
    """Generate a random category name."""
    adjectives = [
        "Red", "Blue", "Green", "Yellow", "Purple", "Orange", "Black", "White",
        "Fast", "Slow", "Big", "Small", "Loud", "Quiet", "Smart", "Clever",
        "Bright", "Dark", "Shiny", "Dull", "Smooth", "Rough", "Soft", "Hard",
        "Hot", "Cold", "Warm", "Cool", "Sweet", "Sour", "Bitter", "Salty",
        "Happy", "Sad", "Angry", "Calm", "Excited", "Bored", "Tired", "Energetic",
        "Ancient", "Modern", "Vintage", "Futuristic", "Classic", "Trendy", "Retro", "Contemporary",
        "Tall", "Short", "Long", "Wide", "Narrow", "Thick", "Thin", "Round",
        "Square", "Triangular", "Rectangular", "Circular", "Oval", "Hexagonal", "Octagonal", "Cylindrical"
    ]
    nouns = [
        "Cat", "Dog", "Bird", "Fish", "Car", "Bike", "Book", "Phone",
        "Computer", "House", "Tree", "Mountain", "River", "Ocean", "Sky", "Star",
        "Lion", "Tiger", "Bear", "Wolf", "Fox", "Deer", "Rabbit", "Squirrel",
        "Eagle", "Hawk", "Falcon", "Owl", "Penguin", "Dolphin", "Whale", "Shark",
        "Plane", "Train", "Boat", "Ship", "Rocket", "Helicopter", "Submarine", "Spaceship",
        "Chair", "Table", "Desk", "Bed", "Sofa", "Lamp", "Clock", "Mirror",
        "Diamond", "Ruby", "Emerald", "Sapphire", "Pearl", "Gold", "Silver", "Bronze",
        "Castle", "Palace", "Tower", "Bridge", "Tunnel", "Temple", "Cathedral", "Pyramid"
    ]

    return f"{random.choice(adjectives)}-{random.choice(nouns)}"

def distribute_urls(urls: List[str], num_categories: int) -> Tuple[List[Tuple[str, List[str]]], List[str]]:
    """
    Distribute URLs across categories.

    Returns:
        Tuple containing:
        - List of tuples (category_name, list_of_urls)
        - List of uncategorized URLs
    """
    # Generate unique category names
    category_names = []
    used_names = set()

    while len(category_names) < num_categories:
        name = generate_random_category_name()
        if name not in used_names:
            category_names.append(name)
            used_names.add(name)

    # Create a copy of URLs to distribute
    remaining_urls = urls.copy()

    # Decide how many URLs will be uncategorized (10-20% of total)
    num_uncategorized = max(1, int(len(urls) * random.uniform(0.1, 0.2)))
    uncategorized_urls = random.sample(remaining_urls, num_uncategorized)

    # Remove uncategorized URLs from the pool
    for url in uncategorized_urls:
        remaining_urls.remove(url)

    # Prepare categories with URLs
    categories = []

    # Select one random category to have no URLs
    empty_category_index = random.randrange(num_categories)

    # Distribute remaining URLs among categories (except the empty one)
    for i in range(num_categories):
        category_name = category_names[i]

        if i == empty_category_index:
            # This is our empty category
            categories.append((category_name, []))
        else:
            # Calculate how many URLs to assign to this category
            # The last category gets all remaining URLs
            if i == num_categories - 1 and i != empty_category_index:
                category_urls = remaining_urls
            else:
                # Randomly assign 1 to 1/3 of remaining URLs to this category
                max_urls = max(1, len(remaining_urls) // 3)
                num_urls = random.randint(1, max_urls) if remaining_urls else 0
                category_urls = random.sample(remaining_urls, min(num_urls, len(remaining_urls)))

            # Remove assigned URLs from the pool
            for url in category_urls:
                if url in remaining_urls:
                    remaining_urls.remove(url)

            categories.append((category_name, category_urls))

    return categories, uncategorized_urls

def generate_local_db(num_urls: int, num_categories: int) -> str:
    """
    Generate a local DB string with the specified number of URLs and categories.

    Args:
        num_urls: Number of URLs to generate
        num_categories: Number of categories to generate

    Returns:
        String containing the local DB content
    """
    # Generate random URLs
    urls = [generate_random_url() for _ in range(num_urls)]

    # Distribute URLs across categories
    categories, uncategorized_urls = distribute_urls(urls, num_categories)

    # Generate the DB string
    db_lines = []

    # Add categories with their URLs
    for category_name, category_urls in categories:
        db_lines.append(f'define category "{category_name}"')
        if not category_urls:
            db_lines.append('\t; no content for this category')
        else:
            for url in category_urls:
                db_lines.append(f'\t{url}')
        db_lines.append('end')
        db_lines.append('')

    # Add uncategorized URLs at the end
    if uncategorized_urls:
        db_lines.append('; Uncategorized URLs:')
        for url in uncategorized_urls:
            db_lines.append(url)

    return '\n'.join(db_lines)

def main():
    parser = argparse.ArgumentParser(description='Generate a local DB file with random URLs and categories.')
    parser.add_argument('--urls', type=int, default=20, help='Number of URLs to generate (default: 20)')
    parser.add_argument('--categories', type=int, default=5, help='Number of categories to generate (default: 5)')
    parser.add_argument('--output', type=str, default='data/local_db.txt', help='Output file path (default: data/local_db.txt)')

    args = parser.parse_args()

    # Validate inputs
    if args.urls < 1:
        print("Error: Number of URLs must be at least 1")
        return

    if args.categories < 2:  # Need at least 2 categories (one empty, one with URLs)
        print("Error: Number of categories must be at least 2")
        return

    # Generate the DB content
    db_content = generate_local_db(args.urls, args.categories)

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    # Write to the output file
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(db_content)

    print(f"Generated local DB with {args.urls} URLs and {args.categories} categories")
    print(f"Output written to {args.output}")

if __name__ == "__main__":
    main()
