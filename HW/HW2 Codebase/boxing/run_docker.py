import asyncio as aio
from argparse import ArgumentParser

async def build_image(image_tag: str, silent: bool = True) -> int:
  print('Building image')
  build_proc = await aio.create_subprocess_exec(
    'docker', 'build', '-t', image_tag, '.',
    stdout=aio.subprocess.DEVNULL if silent else None
  )
  return await build_proc.wait()

async def create_docker_volume(vol_name: str) -> int:
  exists_proc = await aio.create_subprocess_exec('docker', 'volume', 'ls', '-q', stdout=aio.subprocess.PIPE)
  stdout, _ = await exists_proc.communicate()
  stdout = stdout.decode().split('\n')

  try:
    stdout.index(vol_name)
    print(f'Docker volume {vol_name} already exists')
    return 0
  except ValueError:
    pass

  print(f'Creating docker volume at {vol_name}')
  proc = await aio.create_subprocess_exec('docker', 'volume', 'create', vol_name, stdout=aio.subprocess.DEVNULL)
  retcode = await proc.wait()
  print(f'Created docker volume at {vol_name}')
  return retcode

async def run_docker(build: bool, host_port: int):
  image_tag = 'boxing'
  container_name = f'{image_tag}_container'
  volume_name = 'boxing_volume'

  if build:
    retcode = await build_image(image_tag)
    if retcode != 0:
      exit(retcode)
    else:
      print('Built image')

  retcode = await create_docker_volume(volume_name)
  if retcode != 0:
    exit(retcode)

  ps_proc = await aio.create_subprocess_exec('docker', 'ps', '-qaf', f'name={container_name}', stdout=aio.subprocess.PIPE)
  stdout, _ = await ps_proc.communicate()

  if stdout:
    # stop the running container
    print(f'Running container detected, stopping...')
    stop_proc = await aio.subprocess.create_subprocess_exec('docker', 'stop', container_name, stdout=aio.subprocess.DEVNULL)
    retcode = await stop_proc.wait()

    if retcode != 0:
      print(f'Failed to stop container!')
      return

  # remove the stopped container
  exist_proc = await aio.create_subprocess_exec('docker', 'rm', container_name, stdout=aio.subprocess.DEVNULL)
  await exist_proc.wait()
  
  print(f'Starting docker container under the name "{image_tag}"')
  start_proc = await aio.create_subprocess_exec(
    'docker', 'run',
    '--name', container_name,
    '-v', f'{volume_name}:/app/db',
    '-p', f'{host_port}:5000',
    image_tag
  )
  await start_proc.wait()

def parse_args():
  parser = ArgumentParser()

  parser.add_argument('--build', help='Rebuild the image', action='store_true')
  parser.add_argument('host_port', type=int, help='Host port to bind to', nargs='?', default=8080)

  return parser.parse_args()

if __name__ == '__main__':
  args = parse_args()
  aio.run(run_docker(args.build, args.host_port))