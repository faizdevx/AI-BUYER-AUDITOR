from green_river.competitors.search import (
    search_google,
    clean_search_url,
    is_candidate_url,
)

data = search_google(
    "olive textured knit polo shirt",
    num=10,
)

print("SERP RESULTS:", len(data.get("organic_results", [])))
print()

for result in data.get("organic_results", []):
    url = result.get("link")

    if not isinstance(url, str):
        continue

    cleaned = clean_search_url(url)
    allowed = is_candidate_url(cleaned)

    print("TITLE :", result.get("title"))
    print("URL   :", cleaned)
    print("KEEP  :", allowed)
    print("-" * 80)