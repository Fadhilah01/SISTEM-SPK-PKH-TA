/**
 * SPK PKH SVM - Landing Page Engine (GSAP, Lenis, Custom Cursor, Stacking Cards, Simulator)
 */

document.addEventListener('DOMContentLoaded', () => {
    try {
        initTheme();
    } catch(e) {
        console.error('initTheme error:', e);
    }
    
    try {
        initLoaderAndCursor();
    } catch(e) {
        console.error('initLoaderAndCursor error:', e);
        // Failsafe: hide loader immediately
        const loader = document.getElementById('loader');
        if (loader) loader.style.display = 'none';
    }
    
    try {
        initSmoothScrollAndPinning();
    } catch(e) {
        console.error('initSmoothScrollAndPinning error:', e);
    }
    
    try {
        initSVMSimulator();
    } catch(e) {
        console.error('initSVMSimulator error:', e);
    }
});

/* ─── 1. Tema Warna (Light/Dark) ─── */
function initTheme() {
    const toggleBtn = document.getElementById('themeToggle');
    const toggleIcon = toggleBtn ? toggleBtn.querySelector('i') : null;
    
    // Ambil preferensi
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-bs-theme', savedTheme);
    updateThemeIcon(savedTheme);
    
    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-bs-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-bs-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeIcon(newTheme);
        });
    }
    
    function updateThemeIcon(theme) {
        if (!toggleIcon) return;
        if (theme === 'dark') {
            toggleIcon.className = 'bi bi-sun';
        } else {
            toggleIcon.className = 'bi bi-moon';
        }
    }
}

/* ─── 2. Intro Loader & Custom Cursor ─── */
function initLoaderAndCursor() {
    // Custom Cursor tracking
    const cursor = document.getElementById('cursor');
    
    if (cursor) {
        let mouseX = 0, mouseY = 0;
        let ballX = 0, ballY = 0;
        const speed = 0.15; // inersia/lag
        
        window.addEventListener('mousemove', (e) => {
            mouseX = e.clientX;
            mouseY = e.clientY;
        });
        
        // Loop inersia untuk pergerakan kursor yang smooth
        function animateCursor() {
            let distX = mouseX - ballX;
            let distY = mouseY - ballY;
            
            ballX += distX * speed;
            ballY += distY * speed;
            
            cursor.style.left = ballX + 'px';
            cursor.style.top = ballY + 'px';
            
            requestAnimationFrame(animateCursor);
        }
        animateCursor();
        
        // Hover effects pada elemen interaktif
        const interactiveElements = document.querySelectorAll('a, button, input, [role="button"], .toggle-pill, .download-card, .segmented-item');
        interactiveElements.forEach(el => {
            el.addEventListener('mouseenter', () => {
                cursor.classList.add('cursor-hovered');
            });
            el.addEventListener('mouseleave', () => {
                cursor.classList.remove('cursor-hovered');
            });
        });
    }
    
    // GSAP Loader & Hero Intro Timeline (Rejouice-style staggered words animation)
    const tl = gsap.timeline();
    
    // 1. Teks muncul dari kanan/bawah ke kiri dengan stagger dan blur-reveal
    tl.from('#loader h3', {
        x: 40,
        opacity: 0,
        filter: 'blur(10px)',
        duration: 0.8,
        stagger: 0.12,
        ease: 'power3.out'
    });
    
    // 2. Teks keluar bergeser ke kiri dan memudar stagger
    tl.to('#loader h3', {
        x: -40,
        opacity: 0,
        filter: 'blur(10px)',
        duration: 0.6,
        stagger: 0.08,
        delay: 0.5,
        ease: 'power3.in'
    });
    
    // 3. Loader menghilang
    tl.to('#loader', {
        opacity: 0,
        duration: 0.5,
        ease: 'power3.inOut',
        onComplete: () => {
            const lEl = document.getElementById('loader');
            if (lEl) {
                lEl.style.display = 'none';
                lEl.style.pointerEvents = 'none';
            }
        }
    });
    
    // Animate Hero text
    tl.from('.hero-tag', {
        opacity: 0,
        y: 20,
        duration: 0.6,
        ease: 'power3.out'
    }, '-=0.3');
    
    tl.from('.hero h1 span', {
        opacity: 0,
        y: 40,
        filter: 'blur(10px)',
        stagger: 0.1,
        duration: 1,
        ease: 'power4.out'
    }, '-=0.4');
    
    tl.from('.hero p, .hero-ctas', {
        opacity: 0,
        y: 20,
        stagger: 0.15,
        duration: 0.8,
        ease: 'power3.out'
    }, '-=0.6');
}

/* ─── 3. Smooth Scroll (Lenis) & Stacking Cards (ScrollTrigger) ─── */
function initSmoothScrollAndPinning() {
    gsap.registerPlugin(ScrollTrigger);
    
    // 1. Lenis Smooth Scroll
    const lenis = new Lenis({
        duration: 1.2,
        easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)), // expo out
        direction: 'vertical',
        gestureDirection: 'vertical',
        smooth: true,
        mouseMultiplier: 1,
        smoothTouch: false,
        touchMultiplier: 2,
        infinite: false,
    });
    
    // Hubungkan Lenis dengan ScrollTrigger
    lenis.on('scroll', ScrollTrigger.update);
    
    gsap.ticker.add((time) => {
        lenis.raf(time * 1000);
    });
    gsap.ticker.lagSmoothing(0);
    
    // 2. Pin Stacking Cards (Page 4 - Stacking)
    const pinCards = gsap.utils.toArray('.pin-card');
    
    if (pinCards.length > 0) {
        pinCards.forEach((eachCard, index) => {
            // Pin kartu kecuali kartu terakhir
            if (index < pinCards.length - 1) {
                ScrollTrigger.create({
                    trigger: eachCard,
                    start: 'top top',
                    endTrigger: pinCards[pinCards.length - 1],
                    end: 'top top',
                    pin: true,
                    pinSpacing: false,
                    scrub: true
                });
                
                // Beri efek rotasi 3D dan scale mengecil ketika kartu berikutnya muncul
                ScrollTrigger.create({
                    trigger: pinCards[index + 1],
                    start: 'top bottom',
                    end: 'top top',
                    scrub: true,
                    onUpdate: (self) => {
                        const progress = self.progress;
                        const cardWrapper = eachCard.querySelector('.pin-card-wrapper');
                        
                        gsap.set(cardWrapper, {
                            scale: 1 - progress * 0.08,
                            rotationX: progress * -10,
                            transformOrigin: 'top center'
                        });
                        
                        gsap.set(eachCard.querySelector('.pin-card-overlay'), {
                            opacity: progress * 0.4
                        });
                    }
                });
            }
        });
    }
}

/* ─── 4. SVM Real-Time Simulator ─── */
function initSVMSimulator() {
    const controls = ['penghasilan', 'pekerjaan', 'aset'];
    const toggles = ['ibu_hamil', 'anak_usia_dini', 'anak_sekolah', 'disabilitas', 'lansia'];
    
    const controlLabels = {
        'penghasilan': {
            5: 'Desil 1 (< Rp.500.000)',
            4: 'Desil 2 (Rp.600.000 - 700.000)',
            3: 'Desil 3 (Rp.800.000 - 900.000)',
            2: 'Desil 4 (Rp.1.000.000 - 1.200.000)',
            1: 'Desil 5 (Rp.1.300.000 - 1.500.000)'
        },
        'pekerjaan': {
            5: 'Tidak Bekerja',
            4: 'Pekerja Bebas',
            3: 'Petani/Nelayan',
            2: 'Wiraswasta',
            1: 'PNS/Pegawai Tetap'
        },
        'aset': {
            5: 'Tidak Memiliki Aset',
            4: 'Motor (Harga Jual Rendah)',
            3: 'Motor (Harga Jual Tinggi)',
            2: 'Mobil atau Tanah/Kebun',
            1: 'Mobil dan Tanah/Kebun'
        }
    };
    
    // State simulator
    const state = {
        penghasilan: 3,
        pekerjaan: 3,
        aset: 3,
        ibu_hamil: false,
        anak_usia_dini: false,
        anak_sekolah: false,
        disabilitas: false,
        lansia: false
    };
    
    // Hubungkan segmented controls ke state
    controls.forEach(id => {
        const controlEl = document.getElementById(id + 'Control');
        const descEl = document.getElementById(id + 'Desc');
        
        if (controlEl) {
            const items = controlEl.querySelectorAll('.segmented-item');
            items.forEach(item => {
                item.addEventListener('click', () => {
                    // Hapus kelas aktif
                    items.forEach(x => x.classList.remove('active'));
                    // Tambah kelas aktif ke item yang di-klik
                    item.classList.add('active');
                    
                    const val = parseInt(item.getAttribute('data-val'));
                    state[id] = val;
                    
                    // Update keterangan di bawahnya
                    if (descEl) {
                        descEl.textContent = `Keterangan: ${controlLabels[id][val]}`;
                    }
                });
            });
        }
    });
    
    // Hubungkan toggle UI ke state
    toggles.forEach(id => {
        const toggleEl = document.getElementById(id + 'Toggle');
        
        if (toggleEl) {
            toggleEl.addEventListener('click', () => {
                state[id] = !state[id];
                if (state[id]) {
                    toggleEl.classList.add('active');
                } else {
                    toggleEl.classList.remove('active');
                }
            });
        }
    });
    
    // Hubungkan tombol prediksi
    const btnPredict = document.getElementById('btnPredict');
    if (btnPredict) {
        btnPredict.addEventListener('click', () => {
            runPrediction();
        });
    }
    
    function runPrediction() {
        const gaugeFill = document.getElementById('gaugeFill');
        const gaugeValue = document.getElementById('gaugeValue');
        const resultLabel = document.getElementById('resultLabel');
        const resultProb = document.getElementById('resultProb');
        
        if (!gaugeFill) return;
        
        // Loading state untuk tombol
        if (btnPredict) {
            btnPredict.disabled = true;
            btnPredict.textContent = 'Menganalisis...';
        }
        
        // Reset label & gauge saat mulai analisis
        resultLabel.textContent = "MENGANALISIS...";
        resultLabel.style.color = "var(--text-muted)";
        resultProb.textContent = "Menghubungkan ke model SVM RBF...";
        
        fetch('/api/public-predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(state)
        })
        .then(res => res.json())
        .then(data => {
            // Restore button
            if (btnPredict) {
                btnPredict.disabled = false;
                btnPredict.textContent = 'Analisis Kelayakan (SVM RBF)';
            }
            
            if (data.error) {
                console.error(data.error);
                resultLabel.textContent = "ERROR MODEL";
                resultLabel.style.color = "#ff4d4d";
                resultProb.textContent = data.error;
                return;
            }
            
            const prob = data.probability; // range 0 to 1
            const confidencePct = data.confidence_pct;
            const label = data.label; // Layak / Tidak Layak
            
            // Set gauge fill (dashoffset: 565.48 is empty, 0 is full)
            const circumference = 565.48;
            const offset = circumference - (prob * circumference);
            gaugeFill.style.strokeDashoffset = offset;
            
            // Animasi teks probabilitas
            gaugeValue.textContent = Math.round(confidencePct) + '%';
            
            // Set status label
            resultLabel.textContent = label;
            resultProb.textContent = `Akurasi Keputusan: ${confidencePct}% | Probabilitas Kelas`;
            
            if (label === 'Layak') {
                resultLabel.style.color = 'var(--text-primary)';
            } else {
                resultLabel.style.color = 'var(--text-muted)';
            }
        })
        .catch(err => {
            // Restore button
            if (btnPredict) {
                btnPredict.disabled = false;
                btnPredict.textContent = 'Analisis Kelayakan (SVM RBF)';
            }
            console.error('Fetch error:', err);
            resultLabel.textContent = "KONEKSI ERROR";
            resultLabel.style.color = "#ff4d4d";
            resultProb.textContent = "Gagal menghubungi API server lokal.";
        });
    }
}
