# Daily Work Log - Day 1: Domain Immersion & Monolith Analysis
**Commit Tag**: `Day01_Domain_Immersion`  
**Date**: Day 1  
**Author**: Principal Platform Architect  

## Work Accomplished
1. Conducted comprehensive domain immersion across Card-Present (CP) vs Card-Not-Present (CNP) fraud, EMV, UPI, and tokenisation.
2. Compiled domain glossary with 65+ foundational terms in [`docs/GLOSSARY.md`](file:///docs/GLOSSARY.md).
3. Analyzed the 13.5-year Java/Oracle legacy monolith at ShieldPay; documented architectural pain points and root causes of the Q3 2025 fraud surge (₹53 Cr losses) in [`docs/LEGACY_MONOLITH_ANALYSIS.md`](file:///docs/LEGACY_MONOLITH_ANALYSIS.md).
4. Initiated preliminary event storming covering the end-to-end payment transaction lifecycle.

## Architectural Decisions
- Decided on the Strangler Fig Pattern using an Anti-Corruption Layer (ACL) to de-risk the transition from Tomcat/Oracle to event-driven microservices.
- Enforced cryptographic card hash partitioning across event topics.

## Blockers & Resolutions
- *Challenge*: Balancing batch ML transition with active authorization path.  
  *Resolution*: Adopted scatter-gather gRPC parallel invocation with strict deadlines.
