# Capability framing — exploratory sources

Working research for `capabilities_mockup.html`, authored by Codex for discussion with Cail.
This is not a settled talk outline or speaker script.

## Three questions

Cail proposes organizing around present capabilities, extrapolated capability growth, and eventual limits and consequences.
The inspiration is [Zvi Mowshowitz, The Three AI Pills](https://thezvi.substack.com/p/the-three-ai-pills), with the pill terminology omitted.
The third question remains a bare bullet for now, per Cail's latest direction.
The capabilities plot opens the substantive talk, before the history of early agents and harnesses; the former singularity timeline slide is removed.

## METR measurements

The user supplied `benchmark_results_1_1.yaml`, downloaded on 12 September 2026.
[METR's methodology](https://metr.org/time-horizons/) defines the horizon using expert human task duration at a stated agent success probability.
It is not the elapsed time that an agent runs, and it does not apply uniformly to all intellectual work.
The current suite warns that measurements above 16 human-hours are unreliable.
Any extrapolation shown in the mock-up is conditional and must preserve the distinction between 50% and 80% success.
The deck now embeds our generated chart at `#metr`, using the shared `assets/crete-capabilities/chart.html`.

## Inspiration and unverified coordinates

Cail supplied `HR3u7vnWIAUjAzJ.jpeg` and attributed it to [Luke Leisher](https://x.com/luke_leisher_).
Credit him for inspiration; the original post permalink has not been located.
The image mixes measured METR points, index-derived estimates, an Astra 16-hour point, and an approximately 80-hour Navier–Stokes point on an 80%-success human-duration axis.
No primary support was found for the Astra 16-hour coordinate or the curve labeled 9,600 hours by 2028.
Those coordinates should not be reproduced as measurements.

## Demonstrations outside the benchmark

[OpenAI's Navier–Stokes announcement](https://openai.com/index/navier-stokes-solution/) reports approximately 10,000 concurrent agents in the successful group, a result after 88 elapsed hours, and 17 additional hours for Lean formalization using Astra.
Researchers redirected groups, consolidated intermediate findings, and updated the internal model during the effort.
There is no measured equivalent human completion time; multiplying concurrency by elapsed time would not supply one.
This is relevant evidence about coordinated scientific labor, but not a METR horizon point.

[Hugging Face's technical timeline](https://huggingface.co/blog/agent-intrusion-technical-timeline) reports approximately 17,600 recovered actions across July 9–13, including about 2.5 days inside its infrastructure.
There is no matched human-time baseline or repeated-trial 50% success estimate.
At Cail's request, hollow markers show elapsed-time proxies under the explicit hypothetical assumption that a human could finish in the same time. These do not establish a statistical departure from METR's trend and are not included in its fit. The recovered campaign spans 107 hours 46 minutes; this differs from the longer investigation window and the shorter time inside Hugging Face.

## Swarm scale and cost

[METR's Hugging Face investigation](https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/) contains the agent activity timeline in Figure 8.
Keep wall time, concurrency, and token volume separate: 88 hours multiplied by approximately 10,000 concurrent agents is a constant-concurrency illustration, not measured agent-hours or equivalent human work.
OpenAI reports 130 billion output tokens and 2.7 million messages for Navier–Stokes. At an assumed $50 per million output tokens, output charges would be $6.5 million. This is a retail-price illustration, not actual disclosed experiment cost; input tokens, other compute, and internal model economics are unspecified.

## Daniel Kokotajlo's forecast

In his [80,000 Hours interview](https://80000hours.org/podcast/episodes/daniel-kokotajlo-ai-2040-plan-a/), Kokotajlo gives a median forecast of full AI R&D automation by the end of 2028.
That milestone does not supply a 9,600-hour horizon coordinate.
The [AI Futures Project's August update](https://blog.aifutures.org/p/q25-2026-timelines-update-uplift) says the mapping from time horizon to automated coding is uncertain, including whether any finite horizon corresponds to it.
The update adds coding productivity uplift and revenue as forecasting anchors.
If included, distinguish his milestone forecast from a simple continuation of the measured METR trend.
