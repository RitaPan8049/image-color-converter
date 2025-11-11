// 文件上传和拖放处理
document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('file');
    const dropArea = document.getElementById('dropArea');
    const filePreview = document.getElementById('filePreview');
    const previewImage = document.getElementById('previewImage');
    const fileName = document.getElementById('fileName');
    const colorSlider = document.getElementById('n_colors');
    const colorValue = document.getElementById('colorValue');
    const previewBtn = document.getElementById('previewBtn');
    const uploadForm = document.getElementById('uploadForm');

    // 颜色滑块更新
    colorSlider.addEventListener('input', function() {
        colorValue.textContent = this.value;
    });

    // 文件选择处理
    fileInput.addEventListener('change', function(e) {
        handleFile(this.files[0]);
    });

    // 拖放处理
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, function() {
            dropArea.classList.add('dragover');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, function() {
            dropArea.classList.remove('dragover');
        }, false);
    });

    dropArea.addEventListener('drop', function(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            fileInput.files = files;
            handleFile(files[0]);
        }
    }, false);

    // 处理选择的文件
    function handleFile(file) {
        if (!file) return;

        // 显示文件名
        fileName.textContent = file.name;

        // 显示预览
        const reader = new FileReader();
        reader.onload = function(e) {
            previewImage.src = e.target.result;
            filePreview.style.display = 'block';
        };
        reader.readAsDataURL(file);

        // 隐藏颜色预览
        document.getElementById('colorPreview').style.display = 'none';
    }

    // 预览颜色
    previewBtn.addEventListener('click', function(e) {
        e.preventDefault();

        if (!fileInput.files || fileInput.files.length === 0) {
            alert('请先选择一个图片文件');
            return;
        }

        // 显示加载状态
        const originalText = previewBtn.innerHTML;
        previewBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="spinner"><line x1="12" y1="2" x2="12" y2="6"></line><line x1="12" y1="18" x2="12" y2="22"></line><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"></line><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"></line><line x1="2" y1="12" x2="6" y2="12"></line><line x1="18" y1="12" x2="22" y2="12"></line><line x1="4.93" y1="19.07" x2="7.76" y2="16.24"></line><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"></line></svg> 分析中...';
        previewBtn.disabled = true;

        // 创建 FormData
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('n_colors', colorSlider.value);

        // 发送预览请求
        fetch('/preview', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('错误: ' + data.error);
                return;
            }

            // 显示颜色预览
            displayColors(data.colors);
            document.getElementById('colorPreview').style.display = 'block';

            // 滚动到颜色预览
            document.getElementById('colorPreview').scrollIntoView({
                behavior: 'smooth',
                block: 'nearest'
            });
        })
        .catch(error => {
            alert('预览失败: ' + error.message);
        })
        .finally(() => {
            // 恢复按钮状态
            previewBtn.innerHTML = originalText;
            previewBtn.disabled = false;
        });
    });

    // 显示颜色
    function displayColors(colors) {
        const colorGrid = document.getElementById('colorGrid');
        colorGrid.innerHTML = '';

        colors.forEach((color, index) => {
            const colorItem = document.createElement('div');
            colorItem.className = 'color-item';
            colorItem.innerHTML = `
                <div class="color-box" style="background-color: ${color.hex};"></div>
                <div class="color-info">
                    <strong>颜色 ${index + 1}</strong>
                    <span>${color.hex}</span>
                    <span>${color.rgb}</span>
                </div>
            `;
            colorGrid.appendChild(colorItem);
        });
    }

    // 表单提交时显示加载状态
    uploadForm.addEventListener('submit', function() {
        const submitBtn = uploadForm.querySelector('.btn-primary');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="spinner"><line x1="12" y1="2" x2="12" y2="6"></line><line x1="12" y1="18" x2="12" y2="22"></line><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"></line><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"></line><line x1="2" y1="12" x2="6" y2="12"></line><line x1="18" y1="12" x2="22" y2="12"></line><line x1="4.93" y1="19.07" x2="7.76" y2="16.24"></line><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"></line></svg> 转换中...';
        submitBtn.disabled = true;

        // 3秒后恢复按钮（防止用户等待下载时看到加载状态）
        setTimeout(() => {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }, 3000);
    });
});

// 添加旋转动画
const style = document.createElement('style');
style.textContent = `
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    .spinner {
        animation: spin 1s linear infinite;
    }
`;
document.head.appendChild(style);
