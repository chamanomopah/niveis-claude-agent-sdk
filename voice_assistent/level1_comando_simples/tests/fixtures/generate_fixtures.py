"""
Generate audio test fixtures for E2E voice testing.

This script creates audio files containing wake words, prompts,
and stop words for use in automated testing.

Usage:
    cd voice_assistent/level1_comando_simples
    python tests/fixtures/generate_fixtures.py
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from modules.tts import TTS
from modules.logger import NeroLogger


# Fixture definitions
FIXTURES = {
    "wake_word_nero_ouvir.wav": {
        "text": "NERO OUVIR",
        "description": "Standard wake word phrase"
    },
    "wake_word_nero.wav": {
        "text": "NERO",
        "description": "Alternative short wake word"
    },
    "prompt_qual_temperatura_nero_enviar.wav": {
        "text": "Qual a temperatura em São Paulo? NERO ENVIAR",
        "description": "Query with wake word and stop word"
    },
    "prompt_que_horas_nero_enviar.wav": {
        "text": "Que horas são? NERO ENVIAR",
        "description": "Simple time query with stop word"
    },
    "prompt_capital_brasil_nero_enviar.wav": {
        "text": "Qual a capital do Brasil? NERO ENVIAR",
        "description": "Geography query with stop word"
    },
    "prompt_codigo_fibonacci_nero_enviar.wav": {
        "text": "Crie um código Python para calcular fibonacci de 10. NERO ENVIAR",
        "description": "Code generation request with stop word"
    },
    "prompt_sem_stop_word.wav": {
        "text": "Como está o tempo hoje",
        "description": "Prompt without stop word (for timeout testing)"
    },
    "prompt_codigo_python_nero_enviar.wav": {
        "text": "Crie uma função de soma em Python. NERO ENVIAR",
        "description": "Simple code request with stop word"
    },
}


async def generate_fixtures():
    """Generate all audio fixture files."""
    # Get API keys from environment
    cartesia_key = os.getenv("CARTESIA_API_KEY")

    if not cartesia_key or cartesia_key.startswith("your_"):
        print("❌ Error: CARTESIA_API_KEY not set in .env file")
        print("Get your key from: https://cartesia.ai/")
        return 1

    # Initialize TTS and logger
    logger = NeroLogger(verbose=True)
    tts = TTS(cartesia_key, logger)

    # Create fixtures directory
    fixtures_dir = Path("tests/fixtures")
    fixtures_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Generating {len(FIXTURES)} audio fixture files...")
    logger.info(f"Output directory: {fixtures_dir.absolute()}")

    # Generate each fixture
    success_count = 0
    for filename, fixture in FIXTURES.items():
        output_path = fixtures_dir / filename

        try:
            logger.info(f"Generating: {filename} - {fixture['description']}")

            # Generate audio file
            await tts.falar(
                text=fixture['text'],
                voz="ana",
                output_file=str(output_path)
            )

            # Verify file was created
            if output_path.exists():
                size_kb = output_path.stat().st_size / 1024
                logger.complete(f"✓ Created: {filename} ({size_kb:.1f} KB)")
                success_count += 1
            else:
                logger.error(f"✗ Failed to create: {filename}")

        except Exception as e:
            logger.error(f"Error generating {filename}", e)

    # Summary
    logger.info(f"\n{'='*60}")
    logger.info(f"Fixture generation complete: {success_count}/{len(FIXTURES)} files")
    logger.info(f"{'='*60}")

    # Cleanup TTS resources
    await tts.close()

    return 0 if success_count == len(FIXTURES) else 1


def main():
    """Main entry point."""
    print("=" * 60)
    print("NERO Voice Assistant - Audio Fixture Generator")
    print("=" * 60)
    print()

    exit_code = asyncio.run(generate_fixtures())

    if exit_code == 0:
        print("\n✅ All fixtures generated successfully!")
        print("\nYou can now run E2E tests:")
        print("  pytest tests/e2e/test_voice_e2e.py -v")
    else:
        print("\n⚠️  Some fixtures failed to generate")
        print("Check your API keys and try again")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
