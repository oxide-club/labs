"""VM boundaries: checksums, explicit confirmation and bounded shared paths."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

class Environment(unittest.TestCase):
    def setUp(self):
        path = ROOT / 'templates/make/environment.py'
        self.assertTrue(path.is_file(), 'local VM helper is missing')
        spec = importlib.util.spec_from_file_location('lab_environment', path)
        self.env = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.env)

    def test_digest_rejects_modified_image(self):
        with tempfile.TemporaryDirectory() as temp:
            image = Path(temp) / 'image'
            image.write_bytes(b'original')
            digest = hashlib.sha256(b'original').hexdigest()
            self.env.verify_file(image, digest)
            image.write_bytes(b'changed')
            with self.assertRaises(ValueError):
                self.env.verify_file(image, digest)

    def test_runtime_has_no_network_and_only_scoped_shares(self):
        command = self.env.qemu_command(Path('/tmp/state/session.qcow2'), Path('/tmp/inputs'), Path('/tmp/results'))
        self.assertEqual(command[command.index('-nic')+1], 'none')
        shares = [command[i+1] for i,x in enumerate(command) if x == '-virtfs']
        self.assertEqual(len(shares), 2)
        self.assertIn('readonly=on', shares[0])
        self.assertIn('path=/tmp/inputs,', shares[0])
        self.assertIn('path=/tmp/results,', shares[1])
        self.assertNotIn('hostfwd', ' '.join(command))
        self.assertIn('readonly=on', command[command.index('-drive')+1])

    def test_source_copy_excludes_credentials_build_and_links(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / 'source'; dest = Path(temp) / 'dest'
            (source / 'materials/build').mkdir(parents=True)
            (source / '.aws').mkdir()
            (source / 'materials/program.c').write_text('int main(void){}')
            (source / 'materials/build/program').write_text('binary')
            (source / '.aws/credentials').write_text('secret')
            (source / 'Makefile').write_text('help:')
            self.env.copy_package(source, dest)
            self.assertTrue((dest / 'materials/program.c').is_file())
            self.assertFalse((dest / '.aws').exists())
            self.assertFalse((dest / 'materials/build').exists())
            (source / 'materials/link.c').symlink_to(source / '.aws/credentials')
            with self.assertRaises(ValueError):
                self.env.copy_package(source, Path(temp) / 'dest2')

    def test_guest_command_does_not_accept_host_confirmation(self):
        script = self.env.guest_session()
        # Shell is the real boundary: before confirmation it must exit without action.
        import subprocess
        result = subprocess.run(['sh', '-c', script], input='no\n', text=True,
                                capture_output=True, env={'PATH':'/usr/bin:/bin','OXIDE_DISPOSABLE_VM':'confirmed'})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Recusa', result.stdout + result.stderr)

    def test_seed_configures_offline_alpine_boot(self):
        import tarfile
        with tempfile.TemporaryDirectory() as temp:
            seed = Path(temp)
            self.env.seed_files(seed)
            with tarfile.open(seed / 'oxide.apkovl.tar.gz') as archive:
                names = archive.getnames()
                self.assertIn('etc/inittab', names)
                self.assertIn('etc/.default_boot_services', names)
                script = archive.extractfile('usr/local/bin/oxide-root-session').read().decode()
                self.assertIn('apk add --no-network', script)
                self.assertNotIn('--allow-untrusted', script)
                self.assertIn('su ', script)
                self.assertTrue(all(m.uid == 0 for m in archive.getmembers()))

    def test_ready_state_rejects_changed_recipe_and_assets(self):
        with tempfile.TemporaryDirectory() as temp:
            state = Path(temp)
            config = {'image':{'file':'base.iso','sha256':hashlib.sha256(b'image').hexdigest()}, 'packages':[]}
            (state / 'base.iso').write_bytes(b'image')
            (state / 'vmlinuz-virt').write_bytes(b'kernel')
            (state / 'initramfs-virt').write_bytes(b'initrd')
            self.env.write_ready(config, state)
            self.env.check_ready(config, state)
            (state / 'vmlinuz-virt').write_bytes(b'changed')
            with self.assertRaises(ValueError): self.env.check_ready(config, state)

    def test_cached_asset_is_verified_before_copy(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); cache=root/'cache'; state=root/'state'
            cache.mkdir();state.mkdir()
            record={'file':'base.iso','url':'https://invalid.invalid/base.iso','sha256':hashlib.sha256(b'image').hexdigest()}
            (cache/'base.iso').write_bytes(b'corrupt')
            with self.assertRaises(ValueError): self.env.download(record,state,cache)
            self.assertFalse((state/'base.iso').exists())
            (cache/'base.iso').write_bytes(b'image')
            self.env.download(record,state,cache)
            self.assertEqual((state/'base.iso').read_bytes(),b'image')

    def test_state_lock_rejects_concurrent_cleanup(self):
        with tempfile.TemporaryDirectory() as temp:
            state=Path(temp)/'state'
            with self.env.locked_state(state):
                with self.assertRaises(ValueError):
                    with self.env.locked_state(state): pass

    def test_clean_preserves_foreign_files_and_rejects_symlinks(self):
        with tempfile.TemporaryDirectory() as temp:
            state = Path(temp)
            config = {'image':{'file':'base.iso'},'packages':[]}
            (state / 'base.iso').write_bytes(b'image')
            (state / 'notes.txt').write_text('keep')
            self.env.clean_state(config, state)
            self.assertFalse((state / 'base.iso').exists())
            self.assertEqual((state / 'notes.txt').read_text(), 'keep')
            (state / 'base.iso').symlink_to(state / 'notes.txt')
            with self.assertRaises(ValueError): self.env.clean_state(config, state)
            self.assertEqual((state / 'notes.txt').read_text(), 'keep')

if __name__ == '__main__':
    unittest.main()
