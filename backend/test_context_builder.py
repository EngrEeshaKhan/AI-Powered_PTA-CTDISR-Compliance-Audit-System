
from app.ai.retrieval.context_builder import ContextBuilder


def main():
    builder = ContextBuilder()

    control = {
        "control": "19.1",
        "control_description": (
            "Without prejudice to the provisions of any law "
            "for the time being in force, every Licensee shall "
            "ensure the confidentiality of all information "
            "disclosed by the subscribers under the provisions "
            "of these Regulations."
        ),
        "control_interpretation": (
            "Auditors should inspect security controls "
            "implemented by the licensee to ensure confidentiality "
            "of all the information disclosed by the subscribers. "
            "The auditor can suggest additional security controls "
            "to protect the confidentiality, in case the current "
            "security controls do not seem to be sufficient. "
            "Auditor will also assess if the Need to know principle "
            "is being followed for accessing subscriber data/"
            "information."
        ),
    }

    print("=" * 70)
    print("CONTEXT BUILDER TEST")
    print("=" * 70)

    context = builder.build(
        control=control,
        top_k=5,
    )

    print("\nQUERY:")
    print(context["query"])

    print("\nEVIDENCE COUNTS:")
    print(context["evidence_counts"])

    print("\nTOTAL EVIDENCE:")
    print(context["evidence_count"])

    for evidence_type in [
        "ctdisr_evidence",
        "policy_evidence",
        "advisory_evidence",
        "asset_evidence",
    ]:
        print("\n" + "=" * 70)
        print(evidence_type.upper())
        print("=" * 70)

        evidence = context[evidence_type]

        if not evidence:
            print("No evidence found.")
            continue

        for index, item in enumerate(
            evidence,
            start=1,
        ):
            print(f"\n--- Evidence {index} ---")
            print("Score:", item["score"])
            print("Source:", item["file_name"])
            print("Type:", item["document_type"])
            print("Text:")
            print(item["text"][:500])

    print("\n" + "=" * 70)
    print("LLM CONTEXT")
    print("=" * 70)

    llm_context = builder.build_llm_context(
        context
    )

    print(llm_context[:5000])

    print("\n" + "=" * 70)
    print("TEST COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()
