import qiniu
from info import constants

access_key = constants.QINIU_ACCESS_KEY
secret_key = constants.QINIU_SECRET_KEY
# bucket_name = 'pengboinfo'
bucket_name = 'proxy'


def storage(data):
    if not data:
        return None

    # 上传文件到七牛云
    q = qiniu.Auth(access_key, secret_key)
    token = q.upload_token(bucket_name)
    ret, info = qiniu.put_data(token, None, data)
    if info.status_code == 200:

    # 上传成功
        return ret.get('key')
    else:
        raise Exception('上传文件到七牛云失败')

if __name__ == '__main__':
    file_name = input("输入上传的文件")
    with open(file_name, "rb") as f:
        storage(f.read())