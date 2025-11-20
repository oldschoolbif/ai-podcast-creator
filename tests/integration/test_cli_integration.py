"""
Integration tests for CLI commands - Test CLI functionality end-to-end
These tests exercise CLI code paths directly to improve coverage.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@pytest.mark.integration
class TestCLIIntegration:
    """Integration tests for CLI commands - exercise full CLI code paths."""

    def test_version_command_integration(self, test_config, tmp_path):
        """Test version command exercises full code path."""
        from typer.testing import CliRunner
        from src.cli.main import app
        runner = CliRunner()
        
        # Ensure test_config has required keys
        if "app" not in test_config:
            test_config["app"] = {"name": "AI Podcast Creator", "version": "1.0.0"}
        if "character" not in test_config:
            test_config["character"] = {"name": "Test Character", "voice_type": "gtts"}
        
        with patch("src.cli.main.load_config", return_value=test_config):
            result = runner.invoke(app, ["version"])
            assert result.exit_code == 0

    def test_status_command_integration(self, tmp_path):
        """Test status command exercises full code path."""
        from typer.testing import CliRunner
        from src.cli.main import app
        runner = CliRunner()
        
        fake_gpu = MagicMock()
        fake_gpu.gpu_available = False
        fake_gpu.gpu_name = "CPU"
        fake_gpu.gpu_memory = 0.0

        with (
            patch("src.cli.main.get_gpu_manager", return_value=fake_gpu),
            patch("subprocess.run") as mock_subprocess,
        ):
            mock_subprocess.return_value.returncode = 0
            mock_subprocess.return_value.stdout = "ffmpeg version"
            
            result = runner.invoke(app, ["status"])
            assert result.exit_code == 0

    def test_config_show_integration(self, test_config, tmp_path):
        """Test config --show command."""
        from typer.testing import CliRunner
        from src.cli.main import app
        runner = CliRunner()
        
        with patch("src.cli.main.load_config", return_value=test_config):
            result = runner.invoke(app, ["config", "--show"])
            assert result.exit_code == 0

    def test_config_edit_integration(self, tmp_path):
        """Test config --edit command."""
        from typer.testing import CliRunner
        from src.cli.main import app
        runner = CliRunner()
        result = runner.invoke(app, ["config", "--edit"])
        assert result.exit_code == 0

    def test_config_reset_integration(self, tmp_path):
        """Test config --reset command."""
        from typer.testing import CliRunner
        from src.cli.main import app
        runner = CliRunner()
        result = runner.invoke(app, ["config", "--reset"])
        assert result.exit_code == 0

    def test_config_no_flags_integration(self, tmp_path):
        """Test config command without flags."""
        from typer.testing import CliRunner
        from src.cli.main import app
        runner = CliRunner()
        result = runner.invoke(app, ["config"])
        assert result.exit_code == 0
        assert "Use --show" in result.stdout

    def test_list_command_no_database_integration(self, tmp_path):
        """Test list command when database is not available."""
        from typer.testing import CliRunner
        from src.cli.main import app
        runner = CliRunner()
        
        with patch("src.cli.main.DATABASE_AVAILABLE", False):
            result = runner.invoke(app, ["list"])
            assert result.exit_code == 0
            assert "Database not available" in result.stdout

    def test_list_command_with_database_integration(self, tmp_path):
        """Test list command when database is available."""
        from typer.testing import CliRunner
        from src.cli.main import app
        runner = CliRunner()
        
        with patch("src.cli.main.DATABASE_AVAILABLE", True):
            result = runner.invoke(app, ["list"])
            assert result.exit_code == 0

    def test_cleanup_dry_run_integration(self, test_config, tmp_path):
        """Test cleanup --dry-run command."""
        from typer.testing import CliRunner
        from src.cli.main import app
        runner = CliRunner()
        
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir(parents=True)
        (cache_dir / "test.txt").write_text("test")

        test_config["storage"]["cache_dir"] = str(cache_dir)
        test_config["storage"]["outputs_dir"] = str(tmp_path / "outputs")

        with patch("src.cli.main.load_config", return_value=test_config):
            result = runner.invoke(app, ["cleanup", "--dry-run"])
            assert result.exit_code == 0
            # File should still exist (dry-run doesn't delete)
            assert (cache_dir / "test.txt").exists()

    def test_cleanup_cache_only_integration(self, test_config, tmp_path):
        """Test cleanup --cache-only command."""
        from typer.testing import CliRunner
        from src.cli.main import app
        runner = CliRunner()
        
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir(parents=True)
        (cache_dir / "test.txt").write_text("test")

        outputs_dir = tmp_path / "outputs"
        outputs_dir.mkdir(parents=True)
        (outputs_dir / "output.mp4").write_bytes(b"video")

        test_config["storage"]["cache_dir"] = str(cache_dir)
        test_config["storage"]["outputs_dir"] = str(outputs_dir)

        with (
            patch("src.cli.main.load_config", return_value=test_config),
            patch("src.cli.main.typer.confirm", return_value=True),
        ):
            result = runner.invoke(app, ["cleanup", "--cache-only", "--force"])
            assert result.exit_code == 0
            # Cache should be deleted, outputs should remain
            assert not (cache_dir / "test.txt").exists()
            assert (outputs_dir / "output.mp4").exists()

    def test_cleanup_outputs_only_integration(self, test_config, tmp_path):
        """Test cleanup --outputs-only command."""
        from typer.testing import CliRunner
        from src.cli.main import app
        runner = CliRunner()
        
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir(parents=True)
        (cache_dir / "test.txt").write_text("test")

        outputs_dir = tmp_path / "outputs"
        outputs_dir.mkdir(parents=True)
        (outputs_dir / "output.mp4").write_bytes(b"video")

        test_config["storage"]["cache_dir"] = str(cache_dir)
        test_config["storage"]["outputs_dir"] = str(outputs_dir)

        with (
            patch("src.cli.main.load_config", return_value=test_config),
            patch("src.cli.main.typer.confirm", return_value=True),
        ):
            result = runner.invoke(app, ["cleanup", "--outputs-only", "--force"])
            assert result.exit_code == 0
            # Outputs should be deleted, cache should remain
            assert (cache_dir / "test.txt").exists()
            assert not (outputs_dir / "output.mp4").exists()

    def test_cleanup_nothing_to_clean_integration(self, test_config, tmp_path):
        """Test cleanup when there's nothing to clean."""
        from typer.testing import CliRunner
        from src.cli.main import app
        runner = CliRunner()
        
        cache_dir = tmp_path / "cache"
        outputs_dir = tmp_path / "outputs"

        test_config["storage"]["cache_dir"] = str(cache_dir)
        test_config["storage"]["outputs_dir"] = str(outputs_dir)

        with patch("src.cli.main.load_config", return_value=test_config):
            result = runner.invoke(app, ["cleanup", "--force"])
            assert result.exit_code == 0

    def test_init_command_integration(self, tmp_path):
        """Test init command creates directories."""
        import os
        from typer.testing import CliRunner
        from src.cli.main import app
        runner = CliRunner()
        
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            
            with patch("src.cli.main.DATABASE_AVAILABLE", False):
                result = runner.invoke(app, ["init"])
                
                assert result.exit_code == 0
                # Check directories were created
                assert (tmp_path / "data" / "scripts").exists()
                assert (tmp_path / "data" / "outputs").exists()
                assert (tmp_path / "data" / "cache").exists()
                assert (tmp_path / "data" / "models").exists()
                assert (tmp_path / "logs").exists()
        finally:
            os.chdir(original_cwd)

    def test_init_command_with_database_integration(self, tmp_path):
        """Test init command with database available."""
        import os
        from typer.testing import CliRunner
        from src.cli.main import app
        runner = CliRunner()
        
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            
            with (
                patch("src.cli.main.DATABASE_AVAILABLE", True),
                patch("src.cli.main.init_db") as mock_init_db,
            ):
                result = runner.invoke(app, ["init"])
                
                assert result.exit_code == 0
                mock_init_db.assert_called_once()
        finally:
            os.chdir(original_cwd)

    def test_status_with_gpu_integration(self, tmp_path):
        """Test status command with GPU available."""
        from typer.testing import CliRunner
        from src.cli.main import app
        runner = CliRunner()
        
        fake_gpu = MagicMock()
        fake_gpu.gpu_available = True
        fake_gpu.gpu_name = "Test GPU"
        fake_gpu.gpu_memory = 8.0
        fake_gpu.get_performance_config.return_value = {"use_fp16": True, "use_tf32": True}
        fake_gpu.get_memory_usage.return_value = {
            "allocated_gb": 2.0,
            "free_gb": 6.0,
            "total_gb": 8.0
        }

        mock_torch = MagicMock()
        mock_torch.cuda.get_device_capability.return_value = (8, 0)
        mock_torch.version.cuda = "11.8"
        mock_torch.backends.cudnn.is_available.return_value = True
        mock_torch.backends.cudnn.version.return_value = 8500

        with (
            patch("src.cli.main.get_gpu_manager", return_value=fake_gpu),
            patch("subprocess.run") as mock_subprocess,
            patch.dict("sys.modules", {"torch": mock_torch}),
        ):
            mock_subprocess.return_value.returncode = 0
            mock_subprocess.return_value.stdout = "enable-nvenc"
            
            result = runner.invoke(app, ["status"])
            
            assert result.exit_code == 0

    def test_status_ffmpeg_not_found_integration(self, tmp_path):
        """Test status command when FFmpeg is not found."""
        from typer.testing import CliRunner
        from src.cli.main import app
        runner = CliRunner()
        
        fake_gpu = MagicMock()
        fake_gpu.gpu_available = False

        with (
            patch("src.cli.main.get_gpu_manager", return_value=fake_gpu),
            patch("subprocess.run", side_effect=FileNotFoundError()),
        ):
            result = runner.invoke(app, ["status"])
            
            assert result.exit_code == 0

    def test_generate_face_integration(self, test_config, tmp_path):
        """Test generate-face command."""
        from typer.testing import CliRunner
        from src.cli.main import app
        runner = CliRunner()
        
        fake_gpu = MagicMock()
        fake_gpu.gpu_available = True
        fake_gpu.gpu_name = "NVIDIA RTX 4060"
        fake_gpu.gpu_memory = 8.0

        generated_face = tmp_path / "generated_face.png"
        generated_face.write_bytes(b"face")

        with (
            patch("src.cli.main.load_config", return_value=test_config),
            patch("src.cli.main.get_gpu_manager", return_value=fake_gpu),
            patch("src.core.face_generator.FaceGenerator") as mock_face,
        ):
            mock_instance = MagicMock()
            mock_instance.generate.return_value = generated_face
            mock_face.return_value = mock_instance

            result = runner.invoke(
                app,
                [
                    "generate-face",
                    "professional presenter",
                    "--output",
                    str(tmp_path / "custom_face.png"),
                ],
            )

            assert result.exit_code == 0
            assert "Face generated successfully" in result.stdout
            mock_instance.generate.assert_called_once()

    def test_generate_face_exception_integration(self, test_config, tmp_path):
        """Test generate-face command exception handling."""
        from typer.testing import CliRunner
        from src.cli.main import app
        runner = CliRunner()
        
        fake_gpu = MagicMock()
        fake_gpu.gpu_available = False

        with (
            patch("src.cli.main.load_config", return_value=test_config),
            patch("src.cli.main.get_gpu_manager", return_value=fake_gpu),
            patch("src.core.face_generator.FaceGenerator") as mock_face,
        ):
            mock_face.return_value.generate.side_effect = Exception("Face generation failed")
            
            result = runner.invoke(app, ["generate-face", "test face"])
            
            assert result.exit_code == 1
            assert "Error" in result.stdout

