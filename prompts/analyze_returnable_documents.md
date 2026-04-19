Analyse the customer-issued tender document and determine whether it is a document that the supplier must complete and return as part of the tender submission.

Use the prior returnable detection result as an input signal, but verify whether the content supports that conclusion.

Your tasks are:
1. Confirm whether the document is likely required to be returned
2. Identify the main sections, tables, question groups, declarations, schedules, or response areas
3. For each section, decide whether it is a good candidate for auto-population
4. Classify each section using one of:
   - metadata
   - standard_corporate
   - template
   - generated_response
   - manual_only
5. Suggest the most likely source for auto-population using one of:
   - tender_metadata
   - supplier_profile
   - standard_methodology_library
   - manual
6. Be conservative. If a section is likely to require human judgement, tender-specific commercial input, signatures, pricing, legal review, or commitments, classify it as manual_only
7. If the document is clearly a Statement of Work, draft contract, reference attachment, background reading, conditions of tender, or other non-response reference document, it should generally not be treated as required to return

Practical guidance:
- Supplier details forms often contain metadata and standard corporate fields
- Pricing schedules often require manual completion, even if some headers can be inferred
- Compliance matrices may be partially auto-filled but often need manual review
- Response schedules with narrative questions are often generated_response candidates
- Declarations, signatures, insurances, accreditations, and legal commitments often require manual review
- Corporate capability / experience forms may be partially filled from reusable supplier profile content