from env.env import hosts

from smb.SMBConnection import SMBConnection


def connect(host):
    ''' Connect to SMB share
    '''

    conn = SMBConnection(host['username'], host['password'], host['client'], host['hostname'], domain=host['domain'],
                        use_ntlm_v2 = True)
    conn.connect(host['ip'], host['port'])

    return(conn)


def checkShares(host, conn):

    share_list = []

    for share in conn.listShares():
        share_name = share.name
        if share_name in host['shares']:
            print(f'Matched {share.name}')
            share_list.append (share)

    return(share_list)


def iterShares(share, path, conn):

    files = []
    directories = []
    directories_count = 0
    file_count = 0

    shared_files = conn.listPath(share.name, path)

    for shared_file in shared_files:

        file_name = shared_file.filename
        file_size = shared_file.file_size

        if file_name not in ['.', '..']:

            if shared_file.isDirectory:

                directories_count += 1
                directories.append(
                    {
                        'file_name' : file_name,
                        'file_size' : file_size
                    }
                )

            elif shared_file.isNormal:

                file_count += 1
                files.append(
                    {
                        'file_name' : file_name,
                        'file_size' : file_size
                    }
                )

    result = {
        'directories' : directories,
        'directories_count' : directories_count,
        'files' : files,
        'file_count' : file_count
    }

    return(result)


def subFiles(share, files, conn):

    print(f"{share.name}")
    for directory in files['directories']:
        path = f"/{directory['file_name']}/"
        print(f"|   {directory['file_name']}")
        shared_files = conn.listPath(share.name, path)
        for shared_file in shared_files:
            if shared_file.filename not in ['.', '..']:
                print(f'|   |--{shared_file.filename}')


def run():

    for host in hosts:

        print("Connecting...")
        conn = connect(host)
        share_list = checkShares(host, conn)
    
        for share in share_list:
            files = iterShares(share, '/', conn)
            print('------------------------')
            print(share.name)
            print(f"Directories: {files['directories_count']}")
            print(f"Files: {files['file_count']}")

            files = subFiles(share, files, conn)

            




if __name__ == "__main__":

    run()