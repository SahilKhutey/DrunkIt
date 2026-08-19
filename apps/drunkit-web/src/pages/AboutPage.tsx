import { InfoPage } from "../components/InfoPage";

export function AboutPage() {
  return (
    <InfoPage
      eyebrow="About"
      title="Quick commerce, built for a regulated category."
      intro="DrunkIt applies quick-commerce speed and simplicity to a category that deserves more care than a typical grocery run — with verification built into the platform, not bolted on after the fact."
      sections={[
        {
          heading: "What makes this different",
          body: (
            <p>
              Every listing carries a verified-seller seal, every checkout re-checks eligibility
              server-side at the moment of purchase, and every delivery passes through an explicit
              handoff step before it's marked complete. None of that is decoration — it's enforced
              in the platform itself, the same way it would be for any regulated product.
            </p>
          ),
        },
        {
          heading: "How delivery works",
          body: (
            <p>
              We verify your age and delivery location once. From there, browsing and ordering work
              like any quick-commerce app — except every order still runs through the same
              eligibility and stock checks behind the scenes, every time.
            </p>
          ),
        },
        {
          heading: "Where we operate",
          body: (
            <p>
              Delivery availability depends on state-level regulation, which varies across India.
              If your state isn't shown as serviceable yet, it's because we haven't completed the
              legal review for it — not an oversight.
            </p>
          ),
        },
      ]}
    />
  );
}
