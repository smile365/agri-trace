// 土鸡养殖追溯系统 JavaScript 功能

// 页面导航功能
function navigateToFeedingRecords() {
    document.getElementById('mainPage').classList.remove('active');
    document.getElementById('feedingRecordsPage').classList.add('active');
    console.log('导航到喂养操作记录页面');
}

function navigateToMain() {
    document.getElementById('feedingRecordsPage').classList.remove('active');
    document.getElementById('mainPage').classList.add('active');
    console.log('返回主页面');
}

// 显示图片画廊（暂时只显示提示）
function showImageGallery(recordId) {
    console.log(`查看记录 ${recordId} 的图片画廊`);
    alert(`查看记录 ${recordId} 的多张图片（功能待实现）`);
}

document.addEventListener('DOMContentLoaded', function() {
    // 初始化页面
    initializePage();
    
    // 添加交互效果
    addInteractiveEffects();
    
    // 模拟实时数据更新
    simulateRealTimeUpdates();
});

// 初始化页面
function initializePage() {
    console.log('土鸡养殖追溯系统已加载');
    
    // 设置当前时间为查询时间（可选功能）
    updateQueryTime();
    
    // 添加页面加载动画
    addLoadingAnimation();
}

// 更新查询时间
function updateQueryTime() {
    const timeElement = document.querySelector('.time-text');
    if (timeElement) {
        // 可以选择显示当前时间或保持固定时间
        // const currentTime = new Date().toLocaleString('zh-CN');
        // timeElement.textContent = currentTime;
    }
}

// 添加页面加载动画
function addLoadingAnimation() {
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

// 添加交互效果
function addInteractiveEffects() {
    // 卡片悬停效果
    addCardHoverEffects();
    
    // 图片点击效果
    addImageClickEffects();
    
    // 时间线交互
    addTimelineInteraction();
}

// 卡片悬停效果
function addCardHoverEffects() {
    const cards = document.querySelectorAll('.card');
    
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-4px)';
            this.style.boxShadow = '0 8px 25px rgba(0, 0, 0, 0.15)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.08)';
        });
    });
}

// 图片点击效果
function addImageClickEffects() {
    const images = document.querySelectorAll('.chicken-image, .monitor-image, .certificate, .stage-image');
    
    images.forEach(image => {
        image.addEventListener('click', function() {
            // 添加点击动画
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 150);
            
            // 可以在这里添加图片预览功能
            console.log('图片被点击:', this.alt || '未知图片');
        });
        
        // 添加过渡效果
        image.style.transition = 'transform 0.2s ease';
    });
}

// 时间线交互
function addTimelineInteraction() {
    const timelineItems = document.querySelectorAll('.timeline-item');
    
    timelineItems.forEach((item, index) => {
        item.addEventListener('click', function() {
            // 高亮选中的时间线项目
            timelineItems.forEach(i => i.classList.remove('active'));
            this.classList.add('active');
            
            console.log(`时间线项目 ${index + 1} 被点击`);
        });
    });
}

// 模拟实时数据更新
function simulateRealTimeUpdates() {
    // 模拟温湿度数据更新
    updateEnvironmentData();
    
    // 每30秒更新一次环境数据
    setInterval(updateEnvironmentData, 30000);
}

// 更新环境数据
function updateEnvironmentData() {
    const tempElement = document.querySelector('.env-item .env-value');
    const humidityElement = document.querySelectorAll('.env-item .env-value')[1];
    
    if (tempElement && humidityElement) {
        // 生成随机的温湿度变化（小幅度）
        const currentTemp = parseFloat(tempElement.textContent);
        const currentHumidity = parseFloat(humidityElement.textContent);
        
        const newTemp = (currentTemp + (Math.random() - 0.5) * 2).toFixed(1);
        const newHumidity = (currentHumidity + (Math.random() - 0.5) * 4).toFixed(1);
        
        // 添加更新动画
        animateValueChange(tempElement, newTemp + ' ℃');
        animateValueChange(humidityElement, newHumidity + ' %RH');
    }
}

// 数值变化动画
function animateValueChange(element, newValue) {
    element.style.transition = 'color 0.3s ease';
    element.style.color = '#2a5298';
    
    setTimeout(() => {
        element.textContent = newValue;
        element.style.color = '#333';
    }, 150);
}

// 添加触摸设备支持
function addTouchSupport() {
    // 为移动设备添加触摸反馈
    const interactiveElements = document.querySelectorAll('.card, .feature-item, img');
    
    interactiveElements.forEach(element => {
        element.addEventListener('touchstart', function() {
            this.style.opacity = '0.8';
        });
        
        element.addEventListener('touchend', function() {
            this.style.opacity = '1';
        });
    });
}

// 页面滚动效果
function addScrollEffects() {
    window.addEventListener('scroll', function() {
        const scrolled = window.pageYOffset;
        const header = document.querySelector('.header');
        
        if (scrolled > 50) {
            header.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.15)';
        } else {
            header.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
        }
    });
}

// 初始化触摸支持和滚动效果
document.addEventListener('DOMContentLoaded', function() {
    addTouchSupport();
    addScrollEffects();
});

// 工具函数：格式化数字
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

// 工具函数：获取当前时间
function getCurrentTime() {
    return new Date().toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

// 错误处理
window.addEventListener('error', function(e) {
    console.error('页面发生错误:', e.error);
});

// 页面性能监控
window.addEventListener('load', function() {
    const loadTime = performance.now();
    console.log(`页面加载完成，耗时: ${loadTime.toFixed(2)}ms`);
});