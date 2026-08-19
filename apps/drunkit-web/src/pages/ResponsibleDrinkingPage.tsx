import { InfoPage } from "../components/InfoPage";

export function ResponsibleDrinkingPage() {
  return (
    <InfoPage
      eyebrow="Policy"
      title="Age verification & responsible drinking"
      intro="Regulated products need more than a checkbox. Here's what we actually check, and why."
      sections={[
        {
          heading: "Age verification",
          body: (
            <p>
              We record the state-specific legal drinking age and check it against your provided
              date of birth before any order can be placed — not just displayed. If you're under
              your state's minimum age, you can still browse, but you can't add items to a cart or
              check out.
            </p>
          ),
        },
        {
          heading: "At the door",
          body: (
            <p>
              Delivery includes a controlled handoff step before an order can be marked delivered.
              The specific verification method is set by policy per state and platform requirements.
            </p>
          ),
        },
        {
          heading: "If you or someone you know needs support",
          body: (
            <p>
              This platform doesn't provide medical or counseling advice. If drinking has become a
              concern for you or someone you care about, please reach out to a licensed healthcare
              provider or a local support service.
            </p>
          ),
        },
      ]}
    />
  );
}
