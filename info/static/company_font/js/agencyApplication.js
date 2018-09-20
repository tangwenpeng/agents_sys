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
    console.log(arr.join(''))
    // 代理申请页面
    let userinfoData = window.sessionStorage.getItem('userinfo') //提取sessionStorage里面存储的信息
    $('main').html(template('mainTemplate', { 'userinfo': userinfoData })) //渲染模板

    // 用户注册输入信息验证
    $('.modal-body').find('input').on('blur', function() {
        if ($(this).val().trim() === '' && $(this).next().text()) {
            $(this).next()[0].style.opacity = '1'
        }
    })
    // 验证用户名是否被注册过
    $('.modal-body').find('#username').on('blur', function(){
        let that = $(this)
        let params = {username: $(this).val()}
        $.ajax({
            url: '/passport/checkUser',
            data: JSON.stringify(params),
            dataType: 'json',
            contentType: 'application/json',
            type: 'POST',
            success: (res) => {
                if(res.errno === '4003'){
                    that.next().text(res.errmsg)
                    that.next()[0].style.opacity = 1
                    $('.register').addClass('disable')
                } else {
                    $('.register').removeClass('disable')
                }
            }
        })
    })
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
    // 用户注册清除提示信息
    $('.modal-body').find('input').on('keyup', function() {
        if($(this).hasClass('code_pwd')){
            return false
        }
        if ($(this).val().trim() !== '' && $(this).next().text()) {
            $(this).next()[0].style.opacity = '0'
        }
    })

    // 代理申请输入信息验证
    $('.register-form').find('input').on('blur', function() {
        if ($(this).val().trim() === '' && $(this).next().text()) {
            $(this).next()[0].style.opacity = '1'
        } else {
            $(this).next()[0].style.opacity = '0'
        }
    })

    // 代理申请清除提示信息
    $('.register-form').find('input').on('keyup', function() {
            if ($(this).val().trim() !== '' && $(this).next().text()) {
                $(this).next()[0].style.opacity = '0'
            }
        })

    // 验证微信号是否被注册过
    $('.register-form').find('#wechatID').on('blur', function () {
        let that = $(this)
        let params = {original_wechat: $(this).val()}
        $.ajax({
            url: '/passport/checkUser',
            data: JSON.stringify(params),
            dataType: 'json',
            contentType: 'application/json',
            type: 'POST',
            success: (res) => {
                if(res.errno === '4003') {
                    that.next().text(res.errmsg)
                    that.next()[0].style.opacity = '1'
                    $('.register').addClass('disable')
                }else{
                    $('.register').removeClass('disable')
                }
            }
        })
    })

    // 验证手机号是否注册过
     $('.register-form').find('#phone').on('blur', function () {
        let that = $(this)
        let params = {mobile: $(this).val()}
        $.ajax({
            url: '/passport/checkUser',
            data: JSON.stringify(params),
            dataType: 'json',
            contentType: 'application/json',
            type: 'POST',
            success: (res) => {
                if(res.errno === '4003') {
                    that.next().text(res.errmsg)
                    that.next()[0].style.opacity = '1'
                }
            }
        })
    })
    // 正则表达式验证手机号码
    let REphone = /^1[34578]\d{9}$/
    let REpassword = /^[0-9A-Za-z]{5,20}$/

    // 获取短信验证码
    $('.validate').on('click', function() {
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
        let params = {
            'phone_number':$('#phoneNumber').val().trim()
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
    // 验证密码长度为5-20位
    $('#password').on('blur',function(){
        if(!REpassword.test($(this).val())){
            $(this).next().text('请确保输入的密码长度为5-20位')
            $(this).next()[0].style.opacity = '1'
        }
    })

    // 输入图形验证码将提示信息隐藏
    $('#imagecode').on('keyup', () => {
        $('.error_tip')[0].style.opacity = 0
    })

    // 绑定回车按钮事件
    document.onkeyup = function(event){
        if(!event){
            event = window.event
        }
        if((event.keyCode || event.which)==13){
            if($('#myModal').hasClass('in')){
                $('.register').click()
            }else{
                $('.confirmRegister').click()
             }
        }
    }
    // 注册提交
    $('.register').on('click', () => {
        // 获取用户输入的数据
        let username = $('#username').val()
        let pass = $('#password').val()
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
                    window.location.href = './login.html'
                } else {
                    alert(res.message)
                }
            }
        })
    })

    // 代理申请提交
    $('.confirmRegister').on('click', () => {
        $('.confirmRegister').addClass('disable')
        // 获取数据
        var formdata = new FormData()

        formdata.append('wechatID', $('#wechatID').val())
        formdata.append('phone', $('#phone').val())
        formdata.append('fanNumber', $('#fanNumber').val())
        formdata.append('cmbProvince', $('#cmbProvince').val())
        formdata.append('cmbArea', $('#cmbArea').val())
        formdata.append('cmbCity', $('#cmbCity').val())
        formdata.append('phoneNum', $('#phoneNum').val())
        formdata.append('user_name', $('#user_name').val())
        formdata.append('exampleInputFile', $('#exampleInputFile')[0].files[0])
        formdata.append('payFile', $('#payFile')[0].files[0])
        $('#loading-mask').find('.loading-img').append('<p style="color:red;font-size: 40px;">正在申请中...请稍等</p>')
        $('#loading-mask')[0].style.display = 'block'
        $.ajax({
            url: '/passport/proxy/register',
            data: formdata,
            contentType: false,
            processData: false,
            type: 'POST',
            headers:{
                'X-CSRFToken':getCookie('csrf_token')
            },
            beforeSend: () => {
                if ($('#wechatID').val().trim() === '') {
                    $('#wechatID').next()[0].style.opacity = "1"
                    return false
                } else if ($('#phone').val().trim() === '') {
                    $('#phone').next()[0].style.opacity = "1"
                    return false
                } else if ($('#fanNumber').val().trim() === '') {
                    $('#fanNumber').next()[0].style.opacity = "1"
                    $('#loading-mask')[0].style.display = 'none'
                    $('.confirmRegister').removeClass('disable')
                    return false
                } else if ($('#exampleInputFile').val().trim() === '') {
                    $('#exampleInputFile').next()[0].style.opacity = "1"
                    $('#loading-mask')[0].style.display = 'none'
                    $('.confirmRegister').removeClass('disable')
                    return false
                } else if (!REphone.test($('#phone').val().trim())) {
                    alert('请输入正确的手机号码')
                    $('#loading-mask')[0].style.display = 'none'
                    $('.confirmRegister').removeClass('disable')
                    return false
                }else if($('#exampleInputFile')[0].files[0].name == ''){
                    alert("请选择粉丝量截图图片")
                    $('#loading-mask')[0].style.display = 'none'
                    $('.confirmRegister').removeClass('disable')
                    return false
                } else if($('#payFile')[0].files[0].name == ''){
                    alert("请选择微信收款码图片")
                    $('#loading-mask')[0].style.display = 'none'
                    $('.confirmRegister').removeClass('disable')
                    return false
                }
                else if($('#exampleInputFile')[0].files[0].size/1024/1024>5  || $('#payFile')[0].files[0].size/1024/1024>5){
                    alert("您选择的图片超过5M")
                    $('#loading-mask')[0].style.display = 'none'
                    $('.confirmRegister').removeClass('disable')
                    return false
                }
            },
            success: (res) => {
                if (res.errno == '0') {
                    alert('代理申请提交成功，等待审核..........')
                    $('#loading-mask').find('.loading-img img').next().remove()
                    $('#loading-mask')[0].style.display = 'none'
                    $('.confirmRegister').removeClass('disable')
                    window.location.href = '/'
                } else {
                    alert('代理申请提交失败')
                }
            }
        })
    })
    // 清空注册表单内
    $('.btn-myModal').on('click', function(){
        $('#myModal').find('.modal-body form')[0].reset()
    })
})