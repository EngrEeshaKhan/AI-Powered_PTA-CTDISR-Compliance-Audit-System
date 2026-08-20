
from app.ai.retrieval.retriever import Retriever


def print_results(title, results):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)

    if not results:
        print("NO RESULTS")
        return

    for index, result in enumerate(results, start=1):

        print(f"\n--- Result {index} ---")

        print("Score:")
        print(result.get("score"))

        print("\nMetadata:")
        print(result.get("metadata"))

        # Print chunk text if available
        if "text" in result:
            print("\nText:")
            print(result["text"])

        elif "content" in result:
            print("\nContent:")
            print(result["content"])


def main():

    retriever = Retriever()

    # ---------------------------------------------------------
    # TEST 1: SEARCH ALL DOCUMENT TYPES
    # ---------------------------------------------------------

    results = retriever.search_all(
        query=(
            "NTC information security policy "
            "telecom infrastructure critical assets"
        ),
        top_k=10,
    )

    print_results(
        "TEST 1 - ALL DOCUMENT TYPES",
        results,
    )

    # ---------------------------------------------------------
    # TEST 2: POLICIES
    # ---------------------------------------------------------

    results = retriever.search_policies(
        query=(
            "information security policy "
            "telecom infrastructure scope"
        ),
        top_k=5,
    )

    print_results(
        "TEST 2 - POLICIES",
        results,
    )

    # ---------------------------------------------------------
    # TEST 3: ASSETS
    # ---------------------------------------------------------

    results = retriever.search_assets(
        query=(
            "telecom infrastructure equipment "
            "critical assets asset inventory"
        ),
        top_k=5,
    )

    print_results(
        "TEST 3 - ASSETS",
        results,
    )

    # ---------------------------------------------------------
    # TEST 4: CTDISR
    # ---------------------------------------------------------

    results = retriever.search_ctdisr(
        query=(
            "critical telecom infrastructure "
            "security requirements"
        ),
        top_k=5,
    )

    print_results(
        "TEST 4 - CTDISR",
        results,
    )

    # ---------------------------------------------------------
    # TEST 5: ADVISORIES
    # ---------------------------------------------------------

    results = retriever.search_advisories(
        query=(
            "information security "
            "security requirements"
        ),
        top_k=5,
    )

    print_results(
        "TEST 5 - ADVISORIES",
        results,
    )


if __name__ == "__main__":
    main()
