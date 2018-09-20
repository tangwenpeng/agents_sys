from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

SECRET_KEY = '''-----BEGIN RSA PRIVATE KEY-----
MIICXwIBAAKBgQDOuFOvoK6xnjiFl9dxkGbTvU4fNAjavPTNYTf4RDA6zPkvfE2c
ThNYXwGZv/CHSMSnKFK7l16G29ebQBmgfTFR+cRw3aNGhxF/evaQNX2BfYPUeBSw
9RYQfCy9aW7Rsk0ZViRROvWg+vobkWj/2t4ZcLd2WxZvR/1A9T19u2KgoQIDAQAB
AoGBAIEWcAPjZlO6Rvd9q2baUqv0sf0gREs75e7+v7HD+w4tA4qYp+psgv4TTe+S
AYSpd0wfDRLh4oB6djgXnikvJIU5b13yYHdtx2QgZSOH0/hxp5XSR1FkKMP0UFWH
Zid/3FfYvHJFY/SAkmdie7hA3Cy4zgFWYbibiCqddN9JkuO1AkEA10h18zkt7EW6
YpxsWyz0/P6YivkMr6e8/+dQcsNaN9kbKCttCSxrJLTA1x0KN15hSEN+/x2xdVT4
+c9SO8TIfwJBAPXRQ1xFioTsErZ5Gr7Ghd+rmfUYXa7Th9eY8RWZI6GwBvr4d0o5
ZPLu+YBousDj3SIsoSB9PGxYqYfFsKc7Bt8CQQDVisOsuegKeHPUAtMccXClTyki
mL1zs0+vCtRqscnYodrlMoYaVlwE8eJiviR3HYAjvQfIqLxw5RN+P56TOLOjAkEA
lwbX9PQA1APax2OGjBmanL5om845mLT76/lafaOV4bwtvbo0SFUU8bDjeAJgYyxc
a6ex4y0ul36twe4yx7wbTwJBANNM01YghBvSbq0qkGwsVpfKFcOuThCw2F3NcHNZ
oo5b8aLQLx/wHasFsr8Sa9zrg+87hnbyZWhWStn3uiIt6OU=
-----END RSA PRIVATE KEY-----'''
token_valid_time = 24*3600

def generate_token(username, expiration=token_valid_time):
    '''生成token'''
    serializer = Serializer(SECRET_KEY, expires_in=expiration)
    return serializer.dumps({'username': username})


def verify_token(token):
    """
    解析出token校验
    :param token:  str
    :return:  解析出的dict if true else return False
    """
    serializer = Serializer(SECRET_KEY)
    try:
        data = serializer.loads(token)
    except:
        return False
    return data
