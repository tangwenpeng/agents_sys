$(function () {
    // 登录过的页面显示
    let username = sessionStorage.getItem('userinfo')
    if (username) {
        let str = `<li style="margin-top:23px; margin-left:50px;">
                    欢迎回来，${username}!<button type="button" style="margin-left: 20px; background-color: orange; border:none;border-radius:5px; color:#fff;" id="logout">退出</button>
                    </li>`
        $('#nav').append(str)
    }
    $('#nav').on('click','#logout',function(){
        $.ajax({
            url:'/passport/logout',
            type: 'GET',
            dataType: 'json',
            success: (res) => {
                if(res.errno === '0') {
                    sessionStorage.setItem('userinfo', '')
                    window.location.href = '/'
                }
            }
        })
    })
})