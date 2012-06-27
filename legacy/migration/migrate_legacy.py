from ipdb import launch_ipdb_on_exception

from users import MigrateMemberAuth

# Exception launches ipdb https://github.com/Psycojoker/ipdb#use
with launch_ipdb_on_exception():
    m = MigrateMemberAuth()
    m.migrate_all()
