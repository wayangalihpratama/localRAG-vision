# Feature Specification: Multimodal Vision & Scene Retrieval 🎬

**Author**: John (Product Manager)
**Status**: Approved
**Date**: 2026-05-11

## 1. Summary
Multimodal Vision & Scene Retrieval extends LocalRAG Vision's capabilities to long-form video content (meetings, lectures, demonstrations). The goal is to transform video assets into a searchable, granular knowledge base where users can query both what was *said* (audio) and what was *shown* (visual). To maintain performance on local hardware, the system prioritizes processing speed through intelligent frame-skipping while maintaining high descriptive granularity ("chattiness").

## 2. User Stories
- **US.1**: As a student, I want to upload a 2-hour lecture video and ask "When did the professor start talking about backpropagation?" so I can jump straight to that moment.
- **US.2**: As a project manager, I want to search for a specific visual event in a recorded meeting (e.g., "Show me when the UI mockup was shared") even if nobody explicitly named it in the audio.
- **US.3**: As a researcher, I want the AI to provide granular descriptions of visual changes in the video so I can understand the context without re-watching the whole clip.

## 4. Functional Requirements (FR)

| ID | Feature | Description | Priority |
| :--- | :--- | :--- | :--- |
| **FR.1** | Video Ingestion | Support MP4 and MOV uploads via the Knowledge Library. | Must |
| **FR.2** | Scene Segmentation | Break videos into segments using **PySceneDetect** (Content Detector). | Must |
| **FR.3** | High-Speed VLM | Use **LLaVA 7b v1.6** to generate descriptions of keyframes. | Must |
| **FR.4** | Whisper Transcription | Extract and timestamp audio dialogue using **Whisper-base** (or better). | Must |
| **FR.5** | Narrative Synthesis | Combine visual descriptions and audio transcripts into a searchable "Scene Narrative". | Must |
| **FR.6** | Temporal Citations | AI responses must cite sources as `[Video Name @ MM:SS]`. | Must |

## 5. Technical Specifications

### 5.1. Vision Processing Pipeline (Speed-Optimized)
1. **Extraction**: Celery worker extracts audio (Whisper) and frames (OpenCV).
2. **Segmentation**: **PySceneDetect** identifies scene boundaries to minimize redundant VLM analysis.
3. **Keyframe Sampling**: Sample the 1st frame of every scene + 1 frame every 30 seconds for long static scenes.
4. **Visual Description**: Sampled frames are sent to **LLaVA 7b** with a specific "Structural Prompt."
5. **Synthesis**: Visual descriptions are merged with Whisper transcripts into a `Scene Narrative` block.

### 5.2. Retrieval Strategy
- **Multimodal Querying**: User queries are embedded and compared against the "Scene Narrative" blocks in LanceDB.
- **Ranking**: Preference is given to blocks where both visual and audio signals align with the user's intent.

## 6. UI/UX Requirements
- **Video Metadata**: Display timestamps in the search results and Knowledge Library.
- **Granular Citations**: Clickable citations that display the `Video Name` and `MM:SS` in the Source Preview sidebar.
- **Visual Snippet**: (Target) Show the keyframe thumbnail in the Source Preview.

## 7. ADR-003: Narrative Synthesis for Retrieval
- **Status**: Accepted
- **Context**: Users search with text, but videos have dual signals (audio/visual). Embedding them separately would require complex late-fusion at query time.
- **Decision**: We synthesize a "Scene Narrative" string: `"[Scene @ MM:SS] Visual: {VLM_DESC} | Audio: {WHISPER_TRANSCRIPT}"`. We embed this single string to capture the full semantic context of the scene.
- **Consequences**: Simplified search logic; improved retrieval quality through contextual overlap.

## 7. Acceptance Criteria (AC)
- [ ] Successful ingestion of a 10-minute MP4 file with >80% transcription accuracy.
- [ ] AI correctly identifies a visual event (e.g., "A screen was shared") and provides the correct timestamp within 5 seconds of the actual event.
- [ ] Processing time for a 1-minute video segment does not exceed 30 seconds on targeted local hardware.
- [ ] Citations correctly format as `[Filename @ Timestamp]`.

## 8. Out of Scope
- Integrated video player (Phase 2.5).
- Real-time video stream analysis (RTSP/Webcam).
