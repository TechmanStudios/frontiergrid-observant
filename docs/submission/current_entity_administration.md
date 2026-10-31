# Current Entity Administrative Reference

Reviewed: 2026-10-28. Applies to future reuse of Observant-SOL proposal drafts.

This reference reconciles administrative facts with the 2026-10-27 SAM.gov activation notice. It does not amend a historical submission, establish that a proposal was submitted, or authorize portal entry, proposal submission, or a federal registration change. SAM activation alone does not verify every proposal certification or solicitation requirement.

## Values for future proposal drafts

| Field | Value for reuse | Evidence and limits |
| --- | --- | --- |
| Legal business / legal offeror name | TECHMAN STUDIOS LLC | SAM activation notice [S1]; use the LLC suffix in legal-name fields. Brand references to Techman Studios in technical prose need no blanket replacement. |
| UEI | MTXPXGQWBWW5 | SAM activation notice [S1]; existing drafts match. |
| CAGE code | 8X4K7 | SAM activation notice [S1]; existing drafts match. |
| SAM registration status | Active, confirmed by SAM.gov on 2026-10-27 | [S1] is a dated official notification, not a live entity-record lookup. |
| SAM annual renewal date | 2027-10-14 (October 14, 2027) | [S1] explicitly calls this the annual renewal date. Do not relabel it as an independently verified expiration date; if a portal specifically asks for expiration, check that field in the current entity record. |
| Primary NAICS | 541715 | Owner-reported SAM update on 2026-09-30 and reconfirmed for this reconciliation [S5]. The activation notice contains no NAICS field. A current SAM entity extract is still needed for independent federal-record verification. |
| Physical business address | 3375 NW 29TH PL, JENNINGS, FL 32053 | DLA's 2026-10-16 message identifies this as the physical address received from SAM [S2]; the owner's 2026-10-18 reply confirms it as correct and complete [S3]. The activation notice itself contains no address. |
| Principal place of business | Jennings, Florida | Owner confirmed current operations at the physical address in [S3]. Keep this distinct from formation state and any proposal-specific performance location. |
| Entity type / formation state | LLC / Alabama | Alabama Secretary of State screenshot supplied in [S3], showing a domestic limited liability company and Alabama as place of formation [S4]; also confirmed by the owner [S5]. This is documentary evidence, not a fresh state-registry lookup. |

## Exact reconciliation of the historical drafts

The original rows remain in place. Apply these replacements to a new working copy when reusing the drafts, subject to the evidence limits above.

| Source field(s) | Historical value | Treatment for future reuse |
| --- | --- | --- |
| Cover: Legal Business Name; intake: Final legal offeror name and Legal business name | Techman Studios | Use TECHMAN STUDIOS LLC. |
| Cover: SAM.gov Status; intake: SAM.gov registration status and SAM.gov status and expiration date | Active with 04/17/2027, or undated active | Use dated active status and annual renewal date 2027-10-14 as separate concepts. The notice supersedes the old renewal/expiration entry; it does not provide an independently named expiration field. |
| Cover: Primary NAICS Code; intake: NAICS code(s), if known | 541511 or 518210; 518210, 541511 | Use owner-reported primary 541715, marked pending current SAM extract verification. Do not infer that the older codes were removed or remain valid secondary codes. |
| Cover and intake: Physical Address | 2987 Gladden Ln W. Alexandria, AL 36250 | Use 3375 NW 29TH PL, JENNINGS, FL 32053 for physical business address. |
| Intake: Principal place of business | Alexandria, Alabama | Use Jennings, Florida. |
| Cover: State of Incorporation; intake: State of organization/incorporation and State/country of formation | Alabama | Retain Alabama as the state of formation. Moving operations to Florida does not establish a change in formation jurisdiction. |
| Cover and intake: UEI and CAGE | MTXPXGQWBWW5 / 8X4K7 | Retain; verified matching identifiers. |

## Fields requiring separate verification or a proposal decision

- **Secondary NAICS selections:** obtain the current SAM extract before presenting 518210, 541511, or any other code as currently registered. The owner-reported primary change does not establish the secondary list.
- **Mailing address:** the existing Jennings address matches the verified physical address. Preserve the historical mailing entry; the reviewed evidence does not independently establish a current mailing-address designation.
- **Remittance address:** the intake lists the Alabama address. A physical-address change does not establish a payment/remittance change. Leave the historical entry intact and verify the intended current remittance address separately, without storing banking details here.
- **Primary place of performance:** the cover lists Alexandria, Calhoun County, Alabama 36250. Preserve this historical proposal field. The owner's statement that current business operations are in Florida does not by itself amend the proposed work location. Confirm the location for any new proposal before replacing this field.
- **Year founded versus formation date:** both drafts say 2022. The supplied state screenshot [S4] shows a formation date of 2021-02-23. These may represent different events; clarify what the requested field means before changing the founding year. Do not silently substitute one for the other.
- **Other administrative and compliance entries:** no new evidence establishes changes to DBA, personnel roles, head count, ownership/certification claims, foreign-person disclosures, work share, support disclosures, cybersecurity/export-control declarations, or data-rights assertions. Leave them unchanged in this reconciliation. The activation notice does not validate these claims.

## Historical preservation and other reuse surfaces

The inspected `main` revision is [23173c1b2e3e08fabe5879c4c6c720041ab3c952](https://github.com/TechmanStudios/frontiergrid-observant/commit/23173c1b2e3e08fabe5879c4c6c720041ab3c952), dated 2026-05-27 UTC and titled "docs: final Phase I proposal submission package and compiled PDFs." That commit title does not independently prove a DSIP submission. No open pull requests were returned during the 2026-10-28 inspection.

- Original [cover sheet](https://github.com/TechmanStudios/frontiergrid-observant/blob/23173c1b2e3e08fabe5879c4c6c720041ab3c952/docs/submission/volume_1_cover_sheet_draft.md) and [intake](https://github.com/TechmanStudios/frontiergrid-observant/blob/23173c1b2e3e08fabe5879c4c6c720041ab3c952/docs/submission/proposal_placeholder_intake.md) are pinned for comparison. This change adds notices and a current reference; it does not replace their historical rows.
- The compiled `volume_1_cover_sheet_draft.pdf` repeats the older legal name, renewal/expiration entry, NAICS choices, Alabama physical address, and Alabama place of performance. Retain it and all existing PDF/DOCX files unchanged. Produce separately named outputs if preparing a new package later.
- The 17 submission Markdown files were reviewed. The conflicting registration entries are concentrated in the cover and intake. Alabama mentions in the technical drafts describe personnel experience and are not current-address fields.
- `scripts/drive_dsip.py` also contains older `legal_name` and `place_perf` defaults, plus a `state` value of `AL`. It is unchanged and was not executed. Do not use those defaults for current portal entry without a separate review; the meaning of `state` must be resolved before assuming it should change to Florida.
- Technical narratives, abstract, evidence baseline, proposal/topic identifiers, historical submission details, budgets, TABA choices, funding assumptions, and compliance declarations remain unchanged. No proposal was submitted and no official registration was altered by this reconciliation.

## Evidence register

Private email links require access to the relevant mailbox. The emails and state screenshot are not copied into this repository.

- **[S1] Official SAM.gov activation notice**, `donotreply@sam.gov`, 2026-10-27: [registration activated](https://mail.google.com/mail/u/?authuser=techmandesign%40gmail.com#all/1a17df28f104f9c3). Establishes the legal name, UEI, CAGE, dated active status, and annual renewal date.
- **[S2] Official DLA CAGE verification request**, `CAGEREVIEW@dla.mil`, 2026-10-16: [SAM-supplied Florida physical address and prior Alabama CAGE address](https://mail.google.com/mail/u/?authuser=techmandesign%40gmail.com#all/1a146e4a0ba68bb7). This request predates activation; it identifies the submitted data, not a standalone final acceptance.
- **[S3] Owner response to DLA**, Bryan Tucker, 2026-10-18: [physical-location confirmation and state-record screenshot](https://mail.google.com/mail/u/?authuser=techmandesign%40gmail.com#all/1a14ee431789e84d). Confirms the Jennings physical operating address and distinguishes the Alabama registered office.
- **[S4] Alabama Secretary of State business entity screenshot**, filename `alSOS-Screenshot 2026-10-12 142352.png`, supplied with [S3] and visually inspected during this reconciliation: Techman Studios LLC, entity 000-836-797, domestic LLC, Alabama place of formation, formation date 02/23/2021, Alabama registered office. Its displayed status is "Exists"; do not infer additional certification or good-standing claims.
- **[S5] Owner-provided information:** primary NAICS changed to 541715 (reported 2026-09-30), and the 2026-10-28 reconciliation instruction confirms that update, Florida operations, and Alabama formation. Primary NAICS remains owner-reported pending a current SAM extract.
