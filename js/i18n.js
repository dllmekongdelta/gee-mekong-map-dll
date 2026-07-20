/* ====================================
   Mekong Delta Mangrove Mapping
   Internationalization (i18n) Module
   ==================================== */

const translations = {
    en: {
        // Header
        title: "Mekong Delta Living Lab Project",
        
        // Navigation
        nav_coverage: "Coverage Map",
        nav_gain: "Gain Map",
        nav_loss: "Loss Map",
        
        // Map titles
        map_coverage_title: "MANGROVE COVERAGE MAP",
        map_gain_title: "MANGROVE GAIN MAP",
        map_loss_title: "MANGROVE LOSS MAP",
        open_fullscreen: "Open Full Screen",
        
        // Info section
        about_title: "About the Maps",
        info_coverage_title: "MANGROVE COVERAGE MAP",
        info_coverage_desc: "This map shows mangrove coverage for different years (ranging from 1988 to 2026). Using the menu in the top-right corner, you can toggle the different layers on and off to look at the mangrove coverage for a specific year.",
        info_gain_title: "MANGROVE GAIN MAP",
        info_gain_desc: "This map shows mangrove gain from 1988 to 2026. The map also displays various human interventions such as sea dikes, breakwaters, and mangrove restoration projects. By clicking on these interventions, you can access additional information. Using the menu in the top-right corner, you can toggle the different layers on and off to explore the data in more detail.",
        info_loss_title: "MANGROVE LOSS MAP",
        info_loss_desc: "This map shows mangrove loss from 1988 to 2026. The map also displays various human interventions such as sea dikes, breakwaters, and mangrove restoration projects. By clicking on these interventions, you can access additional information. The commune boundaries are included as well. Using the menu in the top-right corner, you can toggle the different layers on and off to explore the data in more detail.",
        
        // Footer
        footer_title: "Digital Living Lab"
    },
    vi: {
        // Header
        title: "Dự án Phòng Thí nghiệm Sống Đồng bằng sông Cửu Long",
        
        // Navigation
        nav_coverage: "Bản đồ Phủ",
        nav_gain: "Bản đồ Tăng",
        nav_loss: "Bản đồ Mất",
        
        // Map titles
        map_coverage_title: "Bản đồ Độ phủ Rừng ngập mặn",
        map_gain_title: "Bản đồ Tăng Rừng ngập mặn",
        map_loss_title: "Bản đồ Mất Rừng ngập mặn",
        open_fullscreen: "Mở Toàn màn hình",
        
        // Info section
        about_title: "Giới thiệu về Bản đồ",
        info_coverage_title: "BẢN ĐỒ ĐỘ PHỦ RỪNG NGẬP MẶN",
        info_coverage_desc: "Bản đồ này hiển thị độ phủ rừng ngập mặn qua các năm khác nhau (từ 1988 đến 2026). Sử dụng menu ở góc trên bên phải, bạn có thể bật/tắt các lớp khác nhau để xem độ phủ rừng ngập mặn cho một năm cụ thể.",
        info_gain_title: "Bản đồ Tăng trưởng Rừng ngập mặn",
        info_gain_desc: "Bản đồ này hiển thị sự tăng trưởng rừng ngập mặn từ 1988 đến 2026. Bản đồ cũng hiển thị các công trình can thiệp như đê biển, kè chắn sóng và các dự án phục hồi rừng ngập mặn. Bằng cách nhấp vào các công trình này, bạn có thể xem thêm thông tin chi tiết. Sử dụng menu ở góc trên bên phải để bật/tắt các lớp dữ liệu.",
        info_loss_title: "Bản đồ Suy giảm Rừng ngập mặn",
        info_loss_desc: "Bản đồ này hiển thị sự suy giảm rừng ngập mặn từ 1988 đến 2026. Bản đồ cũng hiển thị các công trình can thiệp như đê biển, kè chắn sóng và các dự án phục hồi rừng ngập mặn. Bằng cách nhấp vào các công trình này, bạn có thể xem thêm thông tin chi tiết. Ranh giới xã cũng được bao gồm. Sử dụng menu ở góc trên bên phải để bật/tắt các lớp dữ liệu.",
        
        // Footer
        footer_title: "Dự án Phòng Thí nghiệm Sống Đồng bằng sông Cửu Long"
    }
};

// Current language
let currentLanguage = 'en';

/**
 * Set the language and update all translated elements
 * @param {string} lang - Language code ('en' or 'vi')
 */
function setLanguage(lang) {
    currentLanguage = lang;
    
    // Save to localStorage
    localStorage.setItem('language', lang);
    
    // Update all elements with data-i18n attribute
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        if (translations[lang] && translations[lang][key]) {
            element.textContent = translations[lang][key];
        }
    });
    
    // Update language toggle buttons
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    const activeBtn = document.querySelector(`.lang-btn[onclick="setLanguage('${lang}')"]`);
    if (activeBtn) {
        activeBtn.classList.add('active');
    }
    
    // Update HTML lang attribute
    document.documentElement.lang = lang === 'vi' ? 'vi' : 'en';
}

/**
 * Get translation for a specific key
 * @param {string} key - Translation key
 * @returns {string} - Translated text
 */
function t(key) {
    return translations[currentLanguage][key] || key;
}

/**
 * Get current language
 * @returns {string} - Current language code
 */
function getCurrentLanguage() {
    return currentLanguage;
}
