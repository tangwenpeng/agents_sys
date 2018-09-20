$(function() {
    let REphone = /^1[34578]\d{9}$/

    // 查询进度提交
    $('.sumbit').on('click', () => {
        if (!REphone.test($('#phoneNumber').val().trim())) {
            alert('请输入正确的手机号码')
            return false
        }
        $.ajax({
            url: '/passport/advance',
            data: JSON.stringify({'phone':$('#phoneNumber').val().trim()}),
            dataType: 'json',
            contentType: 'application/json',
            type: 'POST',
            success: (res) => {
                if (res.errno == '0') {
                    alert(res.errmsg)
                    $('#myModal').modal('hide')
                } else {
                    alert('数据不存在')
                }
            }
        })
    })
})