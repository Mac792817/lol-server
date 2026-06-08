// 联系表单提交
document.addEventListener('DOMContentLoaded', function() {
    const contactForm = document.getElementById('contactForm');

    contactForm.addEventListener('submit', function(e) {
        e.preventDefault();

        // 获取表单数据
        const formData = new FormData(contactForm);
        const data = Object.fromEntries(formData);

        // 简单验证
        if (!data.name || !data.email || !data.subject || !data.message) {
            alert('请填写所有必填项');
            return;
        }

        // 邮箱格式验证
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(data.email)) {
            alert('请输入有效的邮箱地址');
            return;
        }

        // 模拟提交（实际项目中应该发送到服务器）
        alert('感谢您的留言！我们会尽快与您联系。');
        contactForm.reset();
    });

    // 输入框焦点效果
    const inputs = document.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });

        input.addEventListener('blur', function() {
            this.parentElement.classList.remove('focused');
        });
    });
});