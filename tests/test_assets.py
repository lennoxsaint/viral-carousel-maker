from viral_carousel_maker.assets import collect_visual_prompts


def test_collect_visual_prompts_appends_profile_reference_constraints():
    prompts = collect_visual_prompts(
        {
            "profile": {
                "identity_reference_images": {
                    "lennox_dp": "/Users/lennoxsaint/Documents/Growth/Lennox Saint/DP/Display photo final.png"
                },
                "approved_reference_images": [
                    "examples/style-canon/lennox-fwed-blackboard/samples/accepted-contact-sheet.png"
                ],
                "style_canon": {
                    "characters": {
                        "lennox": (
                            "caricature with clear transparent rounded-square glasses, "
                            "neat dark moustache, red shirt, silver chain, rectangle pendant"
                        )
                    },
                    "likeness_rules": [
                        "Render Lennox as a blackboard-style caricature, not a photo sticker."
                    ],
                    "rejection_triggers": [
                        "Reject generic Lennox face or thick black glasses."
                    ],
                },
            },
            "slides": [
                {
                    "id": "hook",
                    "role": "hook",
                    "visual_prompt": "Draw Lennox and Fwed at a chalkboard.",
                }
            ],
        }
    )

    assert len(prompts) == 1
    prompt = prompts[0]["prompt"]
    assert "Display photo final.png" in prompt
    assert "accepted-contact-sheet.png" in prompt
    assert "clear transparent rounded-square glasses" in prompt
    assert "neat dark moustache" in prompt
    assert "not a photo sticker" in prompt
    assert "thick black glasses" in prompt
