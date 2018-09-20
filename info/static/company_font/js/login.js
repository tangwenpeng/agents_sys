function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}
$(function() {
        // 验证码
        var arr = []  // 定义一个空数组用来存储随机验证码

        draw(arr)
        // 封装一个生成rgb随机颜色的函数
        function myColor(){
          let firstColor = Math.ceil(Math.random() * 255)
          let secondColor = Math.ceil(Math.random() * 255)
          let thirdColor = Math.ceil(Math.random() * 255)
          return color = "rgb"+"("+firstColor+","+secondColor+","+thirdColor+")"
        }
        // 封装一个生成随机验证码的函数
       function draw(arr){
        //  画布随机背景颜色
        // $('#codeCanvas')[0].style.backgroundColor = myColor()
          // 获取画布的宽和高
        let canvas_width = $('#codeCanvas').width()
        let canvas_height = $('#codeCanvas').height()
        //  获取画布
        let canvas = $('#codeCanvas')[0]
        // 获取到画布的绘制环境(2d环境)
        let content_text = canvas.getContext('2d')
        canvas.width = canvas_width
        canvas.height = canvas_height
        // 绘制验证码上随机的小点
        for(var i=0; i<60;i++){
          content_text.strokeStyle = myColor() // 小点的填充颜色
          content_text.beginPath() // 开启绘制
          var x = canvas_width * Math.random() // 在画布的范围内随机生成x坐标
          var y = canvas_height * Math.random() // 在画布的范围内随机生成y坐标
          
          content_text.moveTo(x, y)
          content_text.lineTo(x+1,y+1)
          content_text.stroke()
        }
        // 绘制验证码上随机的线条
        for(var i=0; i<=10; i++){
          content_text.strokeStyle = myColor() // 线条的填充颜色
          content_text.beginPath() // 开启绘制
          content_text.moveTo(canvas_width * Math.random(), canvas_height * Math.random())  // 线条开始绘制的坐标
          content_text.lineTo(canvas_width * Math.random(),canvas_height * Math.random())   // 线条终点绘制的坐标
          content_text.stroke()
        }
        // 定义一个数组用来生成随机数
        let random = new Array(0,1,2,3,4,5,6,7,8,9,'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R', 'S','T','U','V','W','X','Y','Z','a','b','c','d','e','f','g',
                                   'h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z')
        for(var i=0; i<=4;i++){
          var index = Math.floor(Math.random() * random.length) // 生成一个随机索引，
          arr[i] = random[index]  // 生成一组验证码，将生成的验证码储存进全局数组中以便后期进行校验
          var text = random[index] //随机生成的内容文本
          var x = 20 + i * 13 //文字在canvas上的x坐标
          var y = 20 + Math.random() * 8 //文字在canvas上的y坐标
          content_text.font = "bold 23px 微软雅黑"  // 文字的样式
      
          content_text.fillStyle = myColor()  // 文字填充的颜色
          content_text.fillText(text,x,y)   // 填充的文字位置
        }
       }
    
        // 点击切换图形验证码
        $('.get_pic_code').on('click', () => {
            draw(arr)
        })
     // 正则表达式验证手机号码
     let REphone = /^1[34578]\d{9}$/
     let REpassword = /^[0-9A-Za-z]{5,20}$/

      // 验证手机号是否注册过
    $('.modal-body').find('#phoneNumber').on('blur', function () {
        let that = $(this)
        let params = {mobile: $(this).val()}
        $.ajax({
            url: '/passport/checkUser',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(params),
            dataType: 'json',
            success: (res) =>{
                if(res.errno === '4003'){
                    that.next().text(res.errmsg)
                    that.next()[0].style.opacity = '1'
                    $('.validate').addClass('disable')
                } else {
                  $('.validate').removeClass('disable')
                }
            }
        })
    })
    // 登录
    $("#login").on('click', () => {
        // 获取用户输入的数据
        let params = {}
        let username = $('#username').val()
        let password = $('#password').val()

        if(REphone.test(username)){
              params = {
            're' : '1',
            'username':username,
            'password':password
             }
        } else {
            params = {
            're':'2',
            'username':username,
            'password':password
            }
        }
        // 发起Ajax请求进行登录
        $.ajax({
            url: '/passport/login',
            type:"POST",
            data: JSON.stringify(params),
            contentType: 'application/json',
            headers:{
                'X-CSRFToken':getCookie('csrf_token')
            },
            befroeSend: () => {
                if (username === '' && username.trim() === '') {
                    alert('请输入用户名')
                    return false
                } else if (password === '' && password.trim() === '') {
                    alert('请输入密码')
                    return false
                }
            },
            success: (res) => {
                if (res.errno == '0'){
                    alert('登陆成功')
                    // 设置sessionStorage
                    sessionStorage.setItem('userinfo', res.username)
                    window.location.href = './agencyApplication.html'
                }else {
                    //做登陆跳转
                    alert(res.errmsg)
                    window.location.href = '../pages/login.html'
                }
            }
        })
    })
    // 修改密码
    $('.retrievePassword').on('click', () => {
        let code = $('#passwordModalCode').val().trim()
        let pass1 = $('#passWord1').val().trim()
        let pass2 = $('#passWord2').val().trim()
        let phone = $('#passwordModalNumber').val().trim()

        let params = {
            'mobile': phone,
            'sms_code': code,
            'new_password': pass1
        }
        $.ajax({
            url:'/passport/retrievePassword',
            data: JSON.stringify(params),
            dataType: 'json',
            type: 'POST',
            contentType: 'application/json',
            headers:{
                'X-CSRFToken':getCookie('csrf_token')
            },
            beforeSend: function () {
                if(code === '') {
                    alert('请输入短信验证')
                    return false
                } else if(pass1!==pass2){
                    alert('两次输入的密码不相同')
                    return false
                } else if(pass1 === '' || pass2===''){
                    alert("请输入密码")
                    return false
                } else if(phone ===''){
                    alert('请输入手机号码')
                    return false
                } else if(!REpassword.test(pass1)){
                    alert('密码长度不足5位，请输入5-20位的密码')
                    return false
                }else if(!REpassword.test(pass2)){
                    alert('核对密码长度不足5位，请输入5-20位的密码')
                    return false
                }
            },
            success: (res) => {
                if(res.errno === '0'){
                    alert('密码修改成功')
                    $('#passwordModal').modal('hide')
                } else {
                    alert(res.errmsg)
                }
            }
        })
    })
    // 绑定回车按钮事件
    document.onkeyup = function(event){
        if(!event){
            event = window.event //IE浏览器
        }
        if((event.keyCode || event.which)==13){
            // 若有弹框注册模块，则将回车事件加给注册模块
            if($('#myModal').hasClass('in')){
                $('.register').click()
            }else{
                // 将回车事件加给登录模块
                $("#login").click()
             }
        }
    }

       // 获取短信验证码
    $('.validate').on('click', function() {
        let params = {}
        // 判断弹框是注册页面还是修改密码
        if($('#myModal').hasClass('in')){
            if (!REphone.test($('#phoneNumber').val().trim())) {
            // 验证用户输入的手机号码是否符合
            alert('请输入正确的手机号码')
            return false
        } else if ($('#imagecode').val().trim() === '') {
            // 验证是否有输入图形验证码
            $('.error_tip')[0].style.opacity = '1'
            return false
        }else if($('#imagecode').val().trim().toLowerCase() !== arr.join('').toLowerCase()){
            alert('请输入正确的验证码')
            draw(arr) // 重新生成随机码
            $('#imagecode').val('') // 清空输入框
            return false
        }
        params = {
            'phone_number':$('#phoneNumber').val().trim()
         }
        } else if($('#passwordModal').hasClass('in')){
            if (!REphone.test($('#passwordModalNumber').val().trim())) {
            // 验证用户输入的手机号码是否符合
            alert('请输入正确的手机号码')
            return false
          }
          params = {
                'phone_number': $('#passwordModalNumber').val().trim()
          }
        }
        // 向后台发送ajax获取验证码
        //TODO ：AJAX获取短信验证
        $.ajax({
          url: '/passport/mobile_code',
          type: 'POST',
          data: JSON.stringify(params),
          contentType: 'application/json',
          headers:{
                'X-CSRFToken':getCookie('csrf_token')
          },
          success:(res) =>{
            if(res.code===1){
              $('#phoneNumber').next().text(res.message)
            }else{
              $('#phoneNumber').next().text(res.message)
            }
          }
        })
        let time = 60
        $(this).addClass('disable');
        $(this).text('重新发送(' + time + 's)');
        _this = $(this);
        var timeId = setInterval(function() {
            time--;
            _this.text('重新发送(' + time + 's)');
            if (time == 0) {
                clearInterval(timeId);
                _this.removeClass('disable');
                _this.text('重新发送');
            }
        }, 1000)
    })
    // 用户注册输入信息验证
    $('.modal-body').find('input').on('blur', function() {
        if ($(this).val().trim() === '' && $(this).next().text()) {
            $(this).next()[0].style.opacity = '1'
        }
    })
    // 验证用户名是否被注册
    $('.modal-body').find('#userName').on('blur', function(){
        let that = $(this)
        let params = {username: $(this).val()}
        $.ajax({
            url: '/passport/checkUser',
            data: JSON.stringify(params),
            contentType: 'application/json',
            dataType: 'json',
            type: 'POST',
            success: (res) => {
                if(res.errno === '4003'){
                    that.next().text(res.errmsg)
                    that.next()[0].style.opacity = '1'
                    $('.register').addClass('disable')
                } else {
                    $('.register').removeClass('disable')
                }
            }
        })
    })
    // 用户注册清除提示信息
    $('.modal-body').find('input').on('keyup', function() {
        if ($(this).val().trim() !== '' && $(this).next().text()) {
            $(this).next()[0].style.opacity = '0'
        }
    })
    // 验证密码长度为5-20位
    $('#password').on('blur',function(){
        if(!REpassword.test($(this).val())){
            $(this).next().text('请确保输入的密码长度为5-20位')
            $(this).next()[0].style.opacity = '1'
        }
    })
  // 注册提交
   $('.register').on('click', () => {
        // 获取用户输入的数据
        let username = $('#userName').val()
        let pass = $('#password1').val()
        let pass2 = $('#password2').val()
        let phoneNumber = $('#phoneNumber').val()
        let validatenumber = $('#code').val()//短信验证码

        //组织参数
        let params = {
            'username':username,
            'password':pass,
            'mobile':phoneNumber,
            'sms_code':validatenumber

        }

        //TODO：注册ajax提交
        $.ajax({
            url: '/passport/register',
            type: 'POST',
            data: JSON.stringify(params),
            contentType: 'application/json',
            headers:{
                'X-CSRFToken':getCookie('csrf_token')
            },
            beforeSend: () => {
                if (username === '' || username.trim() === '') {
                    alert('请输入用户名')
                    return false
                } else if (pass2 === '' || pass2.trim() === '') {
                    alert('请输入密码')
                    return false
                } else if (pass === '' || pass.trim() === '') {
                    alert('请输入密码')
                    return false
                } else if (pass !== pass2) {
                    alert('两次输入的密码不同')
                    return false
                }else if (validatenumber ==='' || validatenumber.trim() ===''){
                    alert('请输入手机接收到的短信验证码')
                    return false
                }else if(!REpassword.test(pass) || !REpassword.test(pass2)){
                    alert('请确保输入的密码长度为5-20位')
                    return false
                }
            },
            success: (res) => {
                if (res.errno == '0') {
                    alert('注册成功')
                    $('#myModalreset')[0].reset()
                    $('#myModal').modal('hide')
                } else {
                    alert(res.message)
                }
            }
        })
    })
    // 清空注册表单信息
    $('.btn-myModal').on('click',function(){
         $('#myModalreset')[0].reset()
    })
})