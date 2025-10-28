# http_handler_js.py

def get_javascript_code(media_type, ext):
    """Returns the complete JavaScript code as a formatted string."""
    
    js_code = f"""
    const elements = {{
      media: document.getElementById("media"),
      container: document.getElementById("container"),
      crop: document.getElementById("crop"),
      aspectSelect: document.getElementById("aspect"),
      customRatio: document.getElementById("customRatio"),
      customW: document.getElementById("customW"),
      customH: document.getElementById("customH"),
      keepAspect: document.getElementById("keepAspect"),
      ratioInfo: document.getElementById("ratioInfo"),
      naturalResInfo: document.getElementById("naturalResInfo"),
      zoomInfo: document.getElementById("zoomInfo"),
      fileSizeInfo: document.getElementById("fileSizeInfo"),
      loadingIndicator: document.getElementById("loadingIndicator"),
      helpModal: document.getElementById("helpModal"),
      contextMenu: document.getElementById("contextMenu"),
      mediaWrapper: document.getElementById("media-wrapper"),
      mediaViewer: document.querySelector(".media-viewer"),
      themeToggle: document.getElementById("themeToggle"),
      body: document.body,
      floatingPreview: document.getElementById("floatingPreview"),
      previewCanvas: document.getElementById("previewCanvas"),
      previewCanvasWrapper: document.querySelector(".preview-canvas-wrapper"),
      previewHeader: document.querySelector(".preview-header"),
      previewSizeInfo: document.getElementById("previewSizeInfo"),
      previewCloseBtn: document.getElementById("previewCloseBtn"),
      previewX: document.getElementById("previewX"),
      previewY: document.getElementById("previewY"),
      previewW: document.getElementById("previewW"),
      previewH: document.getElementById("previewH"),
      actualX: document.getElementById("actualX"),
      actualY: document.getElementById("actualY"),
      actualW: document.getElementById("actualW"),
      actualH: document.getElementById("actualH"),
    }};

    const state = {{
      isDragging: false,
      isResizing: false,
      resizeDirection: '',
      startMouseX: 0,
      startMouseY: 0,
      startCropLeft: 0,
      startCropTop: 0,
      startCropWidth: 0,
      startCropHeight: 0,
      mediaWidth: 0,
      mediaHeight: 0,
      naturalWidth: 0,
      naturalHeight: 0,
      aspectMode: "free",
      aspectRatio: null,
      keepAspect: true,
      isInitialized: false,
      showGrid: false,
      isHelpVisible: false,
      currentTheme: 'dark',
      lastUpdate: 0,
      animationFrame: null,
      mediaType: "{media_type}",
      fileExtension: "{ext}",
      zoom: 1,
      isPinching: false,
      pinchType: '',
      pinchInitialDist: 0,
      pinchInitialZoom: 0,
      pinchInitialWidth: 0,
      pinchInitialHeight: 0,
      pinchInitialLeft: 0,
      pinchInitialTop: 0,
      pinchInitialMid: {{x: 0, y: 0}},
      pinchInitialRelX: 0,
      pinchInitialRelY: 0,
      pinchInitialScrollLeft: 0,
      pinchInitialScrollTop: 0,
      autoScrollActive: false,
      mouseX: 0,
      mouseY: 0,
      isPreviewPinching: false,
      previewPinchInitialDist: 0,
      previewPinchInitialWidth: 0,
      previewPinchInitialHeight: 0,
      holdTimer: null,
      isResizingPreview: false,
      isUpdating: false,
      // --- IMPROVEMENT: State for Panning ---
      isPanning: false,
      panStartX: 0,
      panStartY: 0,
      panStartScrollLeft: 0,
      panStartScrollTop: 0,
      // --- IMPROVEMENT: State for Double Tap ---
      lastTapTime: 0,
      // --- IMPROVEMENT: State for Label Drag ---
      isLabelDragging: false,
      labelDragInput: null,
      labelDragStartX: 0,
      labelDragInitialValue: 0,
    }};
    
    // --- IMPROVEMENT: System Theme Detection ---
    function initializeTheme() {{
        let storedTheme = localStorage.getItem('theme');
        if (!storedTheme) {{
            const prefersLight = window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches;
            storedTheme = prefersLight ? 'light' : 'dark';
        }}
        setTheme(storedTheme);
    }}
    
    function setTheme(theme) {{
        state.currentTheme = theme;
        elements.body.classList.remove('dark-theme', 'light-theme');
        elements.body.classList.add(theme + '-theme');
        localStorage.setItem('theme', theme);
        
        elements.themeToggle.innerHTML = theme === 'dark' ? '☀️' : '🌙'; 
        elements.themeToggle.title = theme === 'dark' ? 'Switch to Light Theme' : 'Switch to Dark Theme';
    }}

    function toggleTheme() {{
        const newTheme = state.currentTheme === 'dark' ? 'light' : 'dark';
        setTheme(newTheme);
    }}

    const utils = {{
      debounce(func, wait) {{
        let timeout;
        return function executedFunction(...args) {{
          const later = () => {{
            clearTimeout(timeout);
            func(...args);
          }};
          clearTimeout(timeout);
          timeout = setTimeout(later, wait);
        }};
      }},
      
      throttle(func, limit) {{
        let inThrottle;
        return function(...args) {{
          if (!inThrottle) {{
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
          }}
        }};
      }},
      
      getEventCoords(e) {{
        if (e.type.startsWith('touch')) {{
            if (e.touches && e.touches.length > 0) {{
                return {{
                    x: e.touches[0].clientX,
                    y: e.touches[0].clientY
                }};
            }}
            // Fallback for touchend events which might not have e.touches
            if (e.changedTouches && e.changedTouches.length > 0) {{
                return {{
                    x: e.changedTouches[0].clientX,
                    y: e.changedTouches[0].clientY
                }};
            }}
            return {{x: 0, y: 0}}; // Return a default if no coords found
        }}
        return {{
          x: e.clientX,
          y: e.clientY
        }};
      }},
      
      gcd(a, b) {{
        return b === 0 ? a : this.gcd(b, a % b);
      }},
      
      formatFileSize(bytes) {{
        const sizes = ['B', 'KB', 'MB', 'GB'];
        if (bytes === 0) return '0 B';
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return (bytes / Math.pow(1024, i)).toFixed(2) + ' ' + sizes[i];
      }},
      
      lerp(start, end, factor) {{
        return start + (end - start) * factor;
      }},

      getDistance(t1, t2) {{
        return Math.sqrt(Math.pow(t2.clientX - t1.clientX, 2) + Math.pow(t2.clientY - t1.clientY, 2));
      }},

      getMidpoint(t1, t2) {{
        return {{
          x: (t1.clientX + t2.clientX) / 2,
          y: (t1.clientY + t1.clientY) / 2
        }};
      }},

      formatTime(seconds) {{
        if (isNaN(seconds) || seconds < 0) return '0:00';
        const totalSeconds = Math.floor(seconds);
        const hours = Math.floor(totalSeconds / 3600);
        const mins = Math.floor((totalSeconds % 3600) / 60);
        const secs = totalSeconds % 60;
        
        if (hours > 0) {{
          return `${{hours}}:${{mins.toString().padStart(2, '0')}}:${{secs.toString().padStart(2, '0')}}`;
        }}
        return `${{mins}}:${{secs.toString().padStart(2, '0')}}`;
      }},
      
      // --- IMPROVEMENT: Haptic Feedback ---
      vibrate(duration = 10) {{
        if (navigator.vibrate) {{
            try {{
                navigator.vibrate(duration);
            }} catch (e) {{
                console.warn("Haptic feedback failed", e);
            }}
        }}
      }}
    }};
    
    // --- IMPROVEMENT: State Persistence (Crop Memory) ---
    function getStorageKey() {{
        // Using file extension and natural dimensions as a proxy for file uniqueness
        if (!state.naturalWidth || !state.naturalHeight || !state.fileExtension) return null;
        return `mediacrop-v1-${{state.fileExtension}}-${{state.naturalWidth}}x${{state.naturalHeight}}`;
    }}

    const saveCropToStorage = utils.debounce(() => {{
        const key = getStorageKey();
        if (!key || !elements.crop) return;
        
        try {{
            const data = {{
                left: elements.crop.style.left,
                top: elements.crop.style.top,
                width: elements.crop.style.width,
                height: elements.crop.style.height,
                zoom: state.zoom
            }};
            localStorage.setItem(key, JSON.stringify(data));
        }} catch (e) {{
            console.warn("Failed to save crop state to localStorage", e);
        }}
    }}, 500);

    function loadCropFromStorage() {{
        const key = getStorageKey();
        if (!key) return false;
        
        try {{
            const data = localStorage.getItem(key);
            if (data) {{
                const {{ left, top, width, height, zoom }} = JSON.parse(data);
                if (left && top && width && height && zoom) {{
                    setMediaZoom(zoom, true); // Set zoom without re-scaling crop box yet
                    setCropDimensions(parseFloat(left), parseFloat(top), parseFloat(width), parseFloat(height));
                    return true;
                }}
            }}
        }} catch (e) {{
            console.warn("Failed to load crop state from localStorage", e);
            localStorage.removeItem(key); // Clear corrupted data
        }}
        return false;
    }}
    
    function updatePreview() {{
        if (!state.isInitialized || state.mediaType === 'unsupported' || !elements.floatingPreview) {{
            if (elements.floatingPreview) elements.floatingPreview.style.display = 'none';
            return;
        }}
        
        if (elements.floatingPreview.style.display === 'none') {{
            elements.floatingPreview.style.display = 'flex';
        }}
        
        const ctx = elements.previewCanvas.getContext('2d');

        if (state.mediaType === 'audio') {{
            const parentWrapper = elements.previewCanvas.parentElement;
            const width = parentWrapper.clientWidth;
            const height = parentWrapper.clientHeight;
            elements.previewCanvas.width = width;
            elements.previewCanvas.height = height;
            
            ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue('--bg-main').trim();
            ctx.fillRect(0, 0, width, height);
            
            ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue('--text-dim').trim();
            ctx.font = `${{Math.min(width, height) * 0.6}}px Arial`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText('🎵', width / 2, height / 2);
            
            elements.previewSizeInfo.textContent = 'Audio';
            return;
        }}

        if (!elements.crop || !elements.media) return;

        const cropLeft = parseFloat(elements.crop.style.left) || 0;
        const cropTop = parseFloat(elements.crop.style.top) || 0;
        const cropWidth = parseFloat(elements.crop.style.width) || 0;
        const cropHeight = parseFloat(elements.crop.style.height) || 0;

        if (cropWidth < 1 || cropHeight < 1) return;

        const scaleX = state.naturalWidth / state.mediaWidth;
        const scaleY = state.naturalHeight / state.mediaHeight;
        const sourceX = cropLeft * scaleX;
        const sourceY = cropTop * scaleY;
        const sourceWidth = cropWidth * scaleX;
        const sourceHeight = cropHeight * scaleY;
        
        if (sourceWidth < 1 || sourceHeight < 1) return;

        elements.previewCanvas.width = Math.round(sourceWidth);
        elements.previewCanvas.height = Math.round(sourceHeight);

        ctx.clearRect(0, 0, elements.previewCanvas.width, elements.previewCanvas.height);
        try {{
            ctx.drawImage(elements.media, sourceX, sourceY, sourceWidth, sourceHeight, 0, 0, elements.previewCanvas.width, elements.previewCanvas.height);
        }} catch (e) {{
            console.error("Canvas drawImage error:", e);
        }}
        
        elements.previewSizeInfo.textContent = `${{Math.round(sourceWidth)}}x${{Math.round(sourceHeight)}}`;
    }}

    function startPreviewRenderLoop() {{
      if (state.animationFrame) cancelAnimationFrame(state.animationFrame);
      function renderLoop() {{
        updatePreview();
        state.animationFrame = requestAnimationFrame(renderLoop);
      }}
      renderLoop();
    }}

    function stopPreviewRenderLoop() {{
      if (state.animationFrame) {{
        cancelAnimationFrame(state.animationFrame);
        state.animationFrame = null;
      }}
    }}

    function initVideoControls() {{
      const video = elements.media;
      const controls = document.getElementById('videoControls');
      if (!video || !controls) return;

      const playPause = document.getElementById('playPause');
      const seekBar = document.getElementById('seekBar');
      const currentTimeEl = document.getElementById('currentTime');
      const durationEl = document.getElementById('duration');
      const playbackSpeed = document.getElementById('playbackSpeed');
      const muteBtn = document.getElementById('muteBtn');
      const volumeBar = document.getElementById('volumeBar');

      function togglePlayPause() {{
        if (video.paused) {{
          video.play().catch(e => console.log('Play error:', e));
        }} else {{
          video.pause();
        }}
      }}

      playPause.addEventListener('click', togglePlayPause);
      video.addEventListener('click', togglePlayPause);

      video.addEventListener('play', () => {{ playPause.textContent = '⏸️'; startPreviewRenderLoop(); }});
      video.addEventListener('pause', () => {{ playPause.textContent = '▶️'; stopPreviewRenderLoop(); }});
      video.addEventListener('ended', () => {{ playPause.textContent = '▶️'; stopPreviewRenderLoop(); video.currentTime = 0; }});

      let isSeeking = false;
      
      seekBar.addEventListener('mousedown', () => {{ isSeeking = true; if(!video.paused) stopPreviewRenderLoop(); }});
      seekBar.addEventListener('mouseup', () => {{ isSeeking = false; if (!video.paused) startPreviewRenderLoop(); }});
      
      seekBar.addEventListener('input', (e) => {{
        const time = (e.target.value / 100) * video.duration;
        if(isFinite(time)) video.currentTime = time;
        currentTimeEl.textContent = utils.formatTime(time);
        updatePreview();
      }});

      video.addEventListener('timeupdate', () => {{
        if (video.duration) {{
            if (!isSeeking) {{
                const value = (video.currentTime / video.duration) * 100;
                seekBar.value = value;
            }}
            currentTimeEl.textContent = utils.formatTime(video.currentTime);
        }}
      }});

      video.addEventListener('loadedmetadata', () => {{
        durationEl.textContent = utils.formatTime(video.duration);
        seekBar.max = 100;
        if (video.videoWidth && video.videoHeight) {{
            elements.naturalResInfo.textContent = `${{video.videoWidth}}×${{video.videoHeight}}`;
        }}
      }});

      playbackSpeed.addEventListener('change', (e) => {{
        video.playbackRate = parseFloat(e.target.value);
      }});

      volumeBar.addEventListener('input', (e) => {{
        video.volume = e.target.value / 100;
        video.muted = video.volume === 0;
        muteBtn.textContent = video.muted ? '🔇' : '🔊';
      }});

      muteBtn.addEventListener('click', () => {{
        video.muted = !video.muted;
        if (!video.muted && video.volume === 0) video.volume = 1;
        if(video.muted) {{ volumeBar.value = 0; }} else {{ volumeBar.value = video.volume * 100; }}
        muteBtn.textContent = video.muted ? '🔇' : '🔊';
      }});

      video.volume = 1;
      muteBtn.textContent = '🔊';
      playPause.textContent = '▶️';
    }}

    function initializeCrop() {{
      requestAnimationFrame(() => {{ 
        if (state.isInitialized) return;

        updateMediaDimensions(); // First, get natural dimensions
        updateFileInfo();
        
        if (state.mediaType === 'image' || state.mediaType === 'video' || state.mediaType === 'unsupported') {{
            // --- IMPROVEMENT: Load from storage BEFORE positioning ---
            const loadedFromStorage = loadCropFromStorage();
            if (!loadedFromStorage) {{
                positionCropBox(); // Position new box only if nothing was loaded
                setMediaZoom(1);
            }}
            updateCropInfo();
        }}
        
        if (state.mediaType === 'video') {{
          initVideoControls();
          elements.container.style.display = 'flex';
          elements.container.style.flexDirection = 'column';
          elements.mediaWrapper.style.flex = '1';
          elements.mediaWrapper.style.minHeight = '200px';
        }} else if (state.mediaType === 'audio') {{
            updatePreview();
        }}
        
        if (state.mediaType === 'image' && elements.media) {{
            elements.naturalResInfo.textContent = `${{elements.media.naturalWidth}}×${{elements.media.naturalHeight}}`;
        }}

        state.isInitialized = true;
        hideLoading();
        
        if (elements.crop) {{
            elements.crop.focus();
        }}
      }});
    }}

    function hideLoading() {{
      elements.loadingIndicator.style.display = 'none';
    }}

    function updateMediaDimensions() {{
        if (elements.media) {{
            state.mediaWidth = elements.media.offsetWidth;
            state.mediaHeight = elements.media.offsetHeight;
        }}
      
        if (state.mediaType === 'unsupported') {{
          state.mediaWidth = 500;
          state.mediaHeight = 300;
          state.naturalWidth = 500;
          state.naturalHeight = 300;
          elements.container.style.width = state.mediaWidth + 'px';
          elements.container.style.height = state.mediaHeight + 'px';
          elements.mediaWrapper.style.width = state.mediaWidth + 'px';
          elements.mediaWrapper.style.height = state.mediaHeight + 'px';
          return;
        }}
        
        if (!elements.media) return;
      
        if (elements.media.tagName === 'IMG') {{
          state.naturalWidth = elements.media.naturalWidth || state.mediaWidth;
          state.naturalHeight = elements.media.naturalHeight || state.mediaHeight;
        }} else if (elements.media.tagName === 'VIDEO') {{
          state.naturalWidth = elements.media.videoWidth || state.mediaWidth;
          state.naturalHeight = elements.media.videoHeight || state.mediaHeight;
        }} else if (elements.media.tagName === 'AUDIO') {{
            state.naturalWidth = 500; 
            state.naturalHeight = 50; 
            elements.container.style.width = 'fit-content';
            elements.container.style.height = 'auto';
            return;
        }} else {{
          state.naturalWidth = state.mediaWidth;
          state.naturalHeight = state.mediaHeight;
        }}
        
        if (elements.media) {{
            state.mediaWidth = elements.media.offsetWidth;
            state.mediaHeight = elements.media.offsetHeight;
        }}

        elements.naturalResInfo.textContent = `${{state.naturalWidth}}×${{state.naturalHeight}}`;
    }}

    function updateFileInfo() {{
      fetch('/file', {{ method: 'HEAD' }})
        .then(response => {{
          const contentLength = response.headers.get('content-length');
          if (contentLength) {{
            elements.fileSizeInfo.textContent = utils.formatFileSize(parseInt(contentLength));
          }} else {{
             elements.fileSizeInfo.textContent = 'N/A';
          }}
        }})
        .catch(() => {{
          elements.fileSizeInfo.textContent = 'Error';
        }});
    }}

    function positionCropBox() {{
      if (state.mediaWidth === 0 || state.mediaHeight === 0 || !elements.crop) return;
      
      const cropWidth = Math.min(200, state.mediaWidth * 0.4);
      const cropHeight = Math.min(150, state.mediaHeight * 0.3);
      
      const centerX = (state.mediaWidth - cropWidth) / 2;
      const centerY = (state.mediaHeight - cropHeight) / 2;
      
      setCropDimensions(centerX, centerY, cropWidth, cropHeight);
    }}

    function setCropDimensions(left, top, width, height, smooth = false) {{
      if (!elements.crop) return;
      
      const oldLeft = parseFloat(elements.crop.style.left) || 0;
      const oldTop = parseFloat(elements.crop.style.top) || 0;
      
      width = Math.max(30, width);
      height = Math.max(30, height);
      
      left = Math.max(0, Math.min(left, state.mediaWidth - width));
      top = Math.max(0, Math.min(top, state.mediaHeight - height));
      
      width = Math.min(width, state.mediaWidth - left);
      height = Math.min(height, state.mediaHeight - top);
      
      // --- IMPROVEMENT: Haptic Feedback on Edge Snap ---
      if ((left === 0 && oldLeft !== 0) || (top === 0 && oldTop !== 0) ||
          (left + width === state.mediaWidth && oldLeft + width !== state.mediaWidth) ||
          (top + height === state.mediaHeight && oldTop + height !== state.mediaHeight)) {{
          utils.vibrate(5); // Short vibration for edge snap
      }}
      
      const cropStyle = elements.crop.style;
      
      if (smooth) {{
        elements.crop.classList.add('smooth-transition');
        setTimeout(() => elements.crop.classList.remove('smooth-transition'), 150);
      }}
      
      cropStyle.left = Math.round(left) + 'px';
      cropStyle.top = Math.round(top) + 'px';
      cropStyle.width = Math.round(width) + 'px';
      cropStyle.height = Math.round(height) + 'px';
      
      updateCropInfo();
      
      // --- IMPROVEMENT: Save to localStorage ---
      saveCropToStorage();
    }}

    function applyAspectRatio(width, height, maintainWidth = true) {{
      if (state.aspectMode === "free" || !state.aspectRatio || isNaN(state.aspectRatio)) {{
        return {{ width, height }};
      }}
      
      if (maintainWidth) {{
        height = Math.round(width / state.aspectRatio);
      }} else {{
        width = Math.round(height * state.aspectRatio);
      }}
      
      return {{ width, height }};
    }}

    function updateCropInfo() {{
      if (!elements.crop || state.isUpdating) return;
      
      state.isUpdating = true; 

      const left = parseInt(elements.crop.style.left) || 0;
      const top = parseInt(elements.crop.style.top) || 0;
      const width = parseInt(elements.crop.style.width) || 0;
      const height = parseInt(elements.crop.style.height) || 0;
      
      elements.previewX.value = left;
      elements.previewY.value = top;
      elements.previewW.value = width;
      elements.previewH.value = height;

      let actualX = 0, actualY = 0, actualW = 0, actualH = 0;
      if (state.naturalWidth && state.naturalHeight && state.mediaWidth && state.mediaHeight) {{
        const scaleX = state.naturalWidth / state.mediaWidth;
        const scaleY = state.naturalHeight / state.mediaHeight;
        
        actualX = Math.round(left * scaleX);
        actualY = Math.round(top * scaleY);
        actualW = Math.round(width * scaleX);
        actualH = Math.round(height * scaleY);
      }}
      
      elements.actualX.value = actualX;
      elements.actualY.value = actualY;
      elements.actualW.value = actualW;
      elements.actualH.value = actualH;

      elements.zoomInfo.textContent = `${{Math.round(state.zoom * 100)}}%`;
      
      if (width && height) {{
        const gcd = utils.gcd(width, height);
        const ratioW = width / gcd;
        const ratioH = height / gcd;
        
        let ratioText = `${{ratioW}}:${{ratioH}}`;
        if (ratioW === ratioH) ratioText = "1:1";
        else if (Math.abs(ratioW/ratioH - 16/9) < 0.05) ratioText = "≈ 16:9";
        else if (Math.abs(ratioW/ratioH - 4/3) < 0.05) ratioText = "≈ 4:3";
        else if (Math.abs(ratioW/ratioH - 3/2) < 0.05) ratioText = "≈ 3:2";
        else {{
            const floatRatio = (width / height).toFixed(2);
            ratioText = `${{floatRatio}}:1`;
        }}
        
        elements.ratioInfo.textContent = ratioText;
      }}
      
      if (state.mediaType === 'image' || (state.mediaType === 'video' && elements.media.paused)) {{
        updatePreview();
      }}
      
      state.isUpdating = false; 
    }}

    function handlePreviewInputChange(e) {{
      if (state.isUpdating) return;
      
      let pX = parseInt(elements.previewX.value) || 0;
      let pY = parseInt(elements.previewY.value) || 0;
      let pW = parseInt(elements.previewW.value) || 0;
      let pH = parseInt(elements.previewH.value) || 0;
      
      setCropDimensions(pX, pY, pW, pH);
    }}

    function handleActualInputChange(e) {{
      if (state.isUpdating) return; 

      if (!state.naturalWidth || !state.naturalHeight || !state.mediaWidth || !state.mediaHeight) return;

      let aX = parseInt(elements.actualX.value) || 0;
      let aY = parseInt(elements.actualY.value) || 0;
      let aW = parseInt(elements.actualW.value) || 0;
      let aH = parseInt(elements.actualH.value) || 0;

      const scaleX = state.naturalWidth / state.mediaWidth;
      const scaleY = state.naturalHeight / state.mediaHeight;

      if (scaleX === 0 || scaleY === 0) return;

      const pX = aX / scaleX;
      const pY = aY / scaleY;
      const pW = aW / scaleX;
      const pH = aH / scaleY;

      setCropDimensions(pX, pY, pW, pH);
    }}

    // --- IMPROVEMENT: Modified setMediaZoom for localStorage ---
    function setMediaZoom(newZoom, initialLoad = false) {{
      if (state.mediaType !== 'image' && state.mediaType !== 'video') return;
      newZoom = Math.max(0.1, Math.min(10, newZoom));
      
      const oldZoom = state.zoom;
      if (newZoom === oldZoom) return;

      const factor = newZoom / oldZoom;
      state.zoom = newZoom;
      
      if (elements.media && state.naturalWidth && state.naturalHeight) {{
        elements.media.style.width = (state.naturalWidth * newZoom) + 'px';
        elements.media.style.height = (state.naturalHeight * newZoom) + 'px';
      }}
      
      // Don't rescale crop box if we are just loading from storage
      if (elements.crop && !initialLoad) {{
        elements.crop.style.left = (parseFloat(elements.crop.style.left) * factor) + 'px';
        elements.crop.style.top = (parseFloat(elements.crop.style.top) * factor) + 'px';
        elements.crop.style.width = (parseFloat(elements.crop.style.width) * factor) + 'px';
        elements.crop.style.height = (parseFloat(elements.crop.style.height) * factor) + 'px';
      }}
      
      updateMediaDimensions();
      updateCropInfo();
      
      // Save zoom state unless it's the initial load (which is handled by setCropDimensions)
      if (!initialLoad) {{
          saveCropToStorage();
      }}
    }}

    const dragHandlers = {{
      start(e) {{
        // --- IMPROVEMENT: Don't drag crop box if panning ---
        if (!elements.crop || e.target.classList.contains('resize-handle') || state.isPanning) return;
        
        e.preventDefault();
        e.stopPropagation();
        
        if (e.type.startsWith('touch') && e.touches.length === 2) {{
          startPinch('crop', e);
          return;
        }} else if (e.type.startsWith('touch') && e.touches.length > 1) {{
          return;
        }}
        
        const coords = utils.getEventCoords(e);
        state.isDragging = true;
        state.startMouseX = coords.x;
        state.startMouseY = coords.y;
        state.startCropLeft = parseFloat(elements.crop.style.left) || 0;
        state.startCropTop = parseFloat(elements.crop.style.top) || 0;
        
        elements.crop.classList.add('dragging');
        
        document.addEventListener('mousemove', dragHandlers.move, {{ passive: false }});
        document.addEventListener('mouseup', dragHandlers.stop);
        document.addEventListener('touchmove', dragHandlers.move, {{ passive: false }});
        document.addEventListener('touchend', dragHandlers.stop);
        
        document.addEventListener('mousemove', updateMousePos);
        document.addEventListener('touchmove', updateMousePosTouch, {{ passive: false }});
        startAutoScroll();
      }},
      
      move: utils.throttle((e) => {{
        if (!state.isDragging) return;
        
        e.preventDefault();
        const coords = utils.getEventCoords(e);
        
        const deltaX = coords.x - state.startMouseX;
        const deltaY = coords.y - state.startMouseY;
        
        let newLeft = state.startCropLeft + deltaX;
        let newTop = state.startCropTop + deltaY;
        
        const currentWidth = parseFloat(elements.crop.style.width) || 0;
        const currentHeight = parseFloat(elements.crop.style.height) || 0;
        
        setCropDimensions(newLeft, newTop, currentWidth, currentHeight);
      }}, 16), // 16ms throttle targets ~60fps
      
      stop() {{
        state.isDragging = false;
        if (elements.crop) elements.crop.classList.remove('dragging');
        
        document.removeEventListener('mousemove', dragHandlers.move);
        document.removeEventListener('mouseup', dragHandlers.stop);
        document.removeEventListener('touchmove', dragHandlers.move);
        document.removeEventListener('touchend', dragHandlers.stop);
        
        document.removeEventListener('mousemove', updateMousePos);
        document.removeEventListener('touchmove', updateMousePosTouch);
        stopAutoScroll();
      }}
    }};

    const resizeHandlers = {{
      start(e) {{
        e.preventDefault();
        e.stopPropagation();
        
        if (state.mediaType === 'audio' || !elements.crop) return;
        
        const coords = utils.getEventCoords(e);
        state.isResizing = true;
        state.resizeDirection = Array.from(e.target.classList).find(cls => cls !== 'resize-handle');
        state.startMouseX = coords.x;
        state.startMouseY = coords.y;
        
        state.startCropLeft = parseFloat(elements.crop.style.left) || 0;
        state.startCropTop = parseFloat(elements.crop.style.top) || 0;
        state.startCropWidth = parseFloat(elements.crop.style.width) || 0;
        state.startCropHeight = parseFloat(elements.crop.style.height) || 0;
        
        document.addEventListener('mousemove', resizeHandlers.move, {{ passive: false }});
        document.addEventListener('mouseup', resizeHandlers.stop);
        document.addEventListener('touchmove', resizeHandlers.move, {{ passive: false }});
        document.addEventListener('touchend', resizeHandlers.stop);
        
        document.addEventListener('mousemove', updateMousePos);
        document.addEventListener('touchmove', updateMousePosTouch, {{ passive: false }});
        startAutoScroll();
      }},
      
      move: utils.throttle((e) => {{
        if (!state.isResizing || !elements.crop) return;
        
        e.preventDefault();
        const coords = utils.getEventCoords(e);
        
        const deltaX = coords.x - state.startMouseX;
        const deltaY = coords.y - state.startMouseY;
        
        const {{ startCropLeft, startCropTop, startCropWidth, startCropHeight, resizeDirection, aspectRatio, aspectMode }} = state;

        let newLeft = startCropLeft;
        let newTop = startCropTop;
        let newWidth = startCropWidth;
        let newHeight = startCropHeight;

        if (resizeDirection.includes('e')) {{
            newWidth = startCropWidth + deltaX;
        }}
        if (resizeDirection.includes('w')) {{
            newWidth = startCropWidth - deltaX;
        }}
        if (resizeDirection.includes('s')) {{
            newHeight = startCropHeight + deltaY;
        }}
        if (resizeDirection.includes('n')) {{
            newHeight = startCropHeight - deltaY;
        }}

        if (state.keepAspect && aspectRatio && aspectMode !== "free") {{
            const isHorizontalHandle = resizeDirection.includes('e') || resizeDirection.includes('w');
            const isVerticalHandle = resizeDirection.includes('n') || resizeDirection.includes('s');

            if (isHorizontalHandle && !isVerticalHandle) {{
                newHeight = newWidth / aspectRatio;
            }} else if (isVerticalHandle && !isHorizontalHandle) {{
                newWidth = newHeight * aspectRatio;
            }} else {{ 
                const horizontalMovement = Math.abs(newWidth - startCropWidth);
                const verticalMovement = Math.abs(newHeight - startCropHeight);
                
                if (horizontalMovement > verticalMovement) {{
                    newHeight = newWidth / aspectRatio;
                }} else {{
                    newWidth = newHeight * aspectRatio;
                }}
            }}
        }}
        
        if (resizeDirection.includes('n')) {{
            newTop = startCropTop + (startCropHeight - newHeight);
        }}
        if (resizeDirection.includes('w')) {{
            newLeft = startCropLeft + (startCropWidth - newWidth);
        }}
        
        setCropDimensions(newLeft, newTop, newWidth, newHeight);
      }}, 16), // 16ms throttle
      
      stop() {{
        state.isResizing = false;
        
        document.removeEventListener('mousemove', resizeHandlers.move);
        document.removeEventListener('mouseup', resizeHandlers.stop);
        document.removeEventListener('touchmove', resizeHandlers.move);
        document.removeEventListener('touchend', resizeHandlers.stop);
        
        document.removeEventListener('mousemove', updateMousePos);
        document.removeEventListener('touchmove', updateMousePosTouch);
        stopAutoScroll();
      }}
    }};
    
    // --- IMPROVEMENT: Panning Handlers ---
    const panHandlers = {{
        start(e) {{
            if (state.mediaType === 'audio') return;
            
            const isTouch = e.type.startsWith('touch');
            const isZoomed = state.zoom > 1;
            
            // Pan conditions:
            // 1. Desktop: Alt key OR Middle mouse button
            // 2. Mobile: 1-finger touch AND zoomed in AND not touching crop box
            const isDesktopPan = !isTouch && (e.altKey || e.button === 1);
            const isMobilePan = isTouch && e.touches.length === 1 && isZoomed && !elements.crop.contains(e.target);
            
            if (!isDesktopPan && !isMobilePan) return;
            
            // Prevent text selection / default browser pan
            e.preventDefault();
            e.stopPropagation();

            state.isPanning = true;
            const coords = utils.getEventCoords(e);
            state.panStartX = coords.x;
            state.panStartY = coords.y;
            state.panStartScrollLeft = elements.mediaViewer.scrollLeft;
            state.panStartScrollTop = elements.mediaViewer.scrollTop;

            elements.mediaViewer.style.cursor = 'grabbing';

            document.addEventListener('mousemove', panHandlers.move, {{ passive: false }});
            document.addEventListener('mouseup', panHandlers.stop);
            document.addEventListener('touchmove', panHandlers.move, {{ passive: false }});
            document.addEventListener('touchend', panHandlers.stop);
        }},
        
        move: utils.throttle((e) => {{
            if (!state.isPanning) return;
            e.preventDefault();
            
            const coords = utils.getEventCoords(e);
            const deltaX = coords.x - state.panStartX;
            const deltaY = coords.y - state.panStartY;
            
            elements.mediaViewer.scrollLeft = state.panStartScrollLeft - deltaX;
            elements.mediaViewer.scrollTop = state.panStartScrollTop - deltaY;
        }}, 16), // 16ms throttle
        
        stop() {{
            state.isPanning = false;
            elements.mediaViewer.style.cursor = 'grab';

            document.removeEventListener('mousemove', panHandlers.move);
            document.removeEventListener('mouseup', panHandlers.stop);
            document.removeEventListener('touchmove', panHandlers.move);
            document.removeEventListener('touchend', panHandlers.stop);
        }}
    }};
    
    function handleMouseWheelZoom(e) {{
      if (state.mediaType === 'audio') return;
      e.preventDefault();

      const zoomFactor = e.deltaY < 0 ? 1.1 : 1 / 1.1;
      const newZoom = state.zoom * zoomFactor;
      
      const viewer = elements.mediaViewer;
      const rect = viewer.getBoundingClientRect();
      
      const relativeX = e.clientX - rect.left;
      const relativeY = e.clientY - rect.top;

      const contentX = viewer.scrollLeft + relativeX;
      const contentY = viewer.scrollTop + relativeY;
      
      const oldZoom = state.zoom;
      setMediaZoom(newZoom);
      
      // Calculate new scroll position to keep zoom centered on mouse
      const newFactor = state.zoom / oldZoom;
      const newContentX = contentX * newFactor;
      const newContentY = contentY * newFactor;

      viewer.scrollLeft = newContentX - relativeX;
      viewer.scrollTop = newContentY - relativeY;
    }}

    function startPinch(type, e) {{
      if (e.touches.length !== 2) return;
      if (type === 'media' && state.mediaType !== 'image' && state.mediaType !== 'video') return;
      
      // Prevent panning if pinching
      state.isPanning = false; 
      
      state.isPinching = true;
      state.pinchType = type;
      state.pinchInitialDist = utils.getDistance(e.touches[0], e.touches[1]);
      
      if (type === 'crop') {{
        state.pinchInitialWidth = parseFloat(elements.crop.style.width);
        state.pinchInitialHeight = parseFloat(elements.crop.style.height);
        state.pinchInitialLeft = parseFloat(elements.crop.style.left);
        state.pinchInitialTop = parseFloat(elements.crop.style.top);
      }} else {{
        state.pinchInitialZoom = state.zoom;
        state.pinchInitialMid = utils.getMidpoint(e.touches[0], e.touches[1]);
        const viewerRect = elements.mediaViewer.getBoundingClientRect();
        state.pinchInitialRelX = state.pinchInitialMid.x - viewerRect.left;
        state.pinchInitialRelY = state.pinchInitialMid.y - viewerRect.top;
        state.pinchInitialScrollLeft = elements.mediaViewer.scrollLeft;
        state.pinchInitialScrollTop = elements.mediaViewer.scrollTop;
      }}
      document.addEventListener('touchmove', handlePinchMove, {{ passive: false }});
      document.addEventListener('touchend', handlePinchEnd);
    }}

    function handlePinchMove(e) {{
      if (!state.isPinching || e.touches.length !== 2) return;
      e.preventDefault();
      
      const newDist = utils.getDistance(e.touches[0], e.touches[1]);
      if (state.pinchInitialDist === 0) return;
      const factor = newDist / state.pinchInitialDist;
      
      if (state.pinchType === 'crop') {{
        let newWidth = state.pinchInitialWidth * factor;
        let newHeight = state.pinchInitialHeight * factor;
        
        if (state.keepAspect && state.aspectRatio && state.aspectMode !== 'free') {{
             const ratio = state.aspectRatio;
            const currentRatio = newWidth / newHeight;
            if (Math.abs(currentRatio - ratio) > 0.01) {{
                 if (Math.abs(newWidth - state.pinchInitialWidth) > Math.abs(newHeight - state.pinchInitialHeight) * ratio) {{
                    newHeight = newWidth / ratio;
                }} else {{
                    newWidth = newHeight * ratio;
                }}
            }}
        }}

        const deltaW = newWidth - state.pinchInitialWidth;
        const deltaH = newHeight - state.pinchInitialHeight;
        const newLeft = state.pinchInitialLeft - deltaW / 2;
        const newTop = state.pinchInitialTop - deltaH / 2;
        
        setCropDimensions(newLeft, newTop, newWidth, newHeight);
      }} else {{ 
        const newZoom = state.pinchInitialZoom * factor;
        const oldZoom = state.zoom;
        setMediaZoom(newZoom);
        
        const newFactor = state.zoom / oldZoom;
        const viewer = elements.mediaViewer;
        
        const contentX = state.pinchInitialScrollLeft + state.pinchInitialRelX;
        const contentY = state.pinchInitialScrollTop + state.pinchInitialRelY;
        
        const newContentX = contentX * newFactor;
        const newContentY = contentY * newFactor;
        
        viewer.scrollLeft = newContentX - state.pinchInitialRelX;
        viewer.scrollTop = newContentY - state.pinchInitialRelY;
      }}
    }}


    function handlePinchEnd() {{
      state.isPinching = false;
      state.pinchType = '';
      document.removeEventListener('touchmove', handlePinchMove);
      document.removeEventListener('touchend', handlePinchEnd);
    }}
    
    function handleMediaTouchStart(e) {{
      // This handles 1-finger pan start (via panHandlers) and 2-finger pinch start
      panHandlers.start(e);
      
      if (e.touches.length === 2 && state.mediaType !== 'audio') {{
        e.preventDefault();
        startPinch('media', e);
      }}
    }}
    
    // --- IMPROVEMENT: Double Tap to Zoom ---
    function handleDoubleTap(e) {{
        if (state.mediaType === 'audio' || state.isPinching || e.touches.length > 0) return;

        const now = new Date().getTime();
        const timeSinceLastTap = now - state.lastTapTime;

        if (timeSinceLastTap < 300 && timeSinceLastTap > 0) {{
            // Double tap detected
            e.preventDefault();
            
            const viewer = elements.mediaViewer;
            
            if (state.zoom > 1) {{
                // Zoom out and center
                setMediaZoom(1);
                const targetScrollLeft = (viewer.scrollWidth - viewer.clientWidth) / 2;
                const targetScrollTop = (viewer.scrollHeight - viewer.clientHeight) / 2;
                viewer.scrollTo({{ left: targetScrollLeft, top: targetScrollTop, behavior: 'smooth' }});
            }} else {{
                // Zoom in at tap location
                const rect = viewer.getBoundingClientRect();
                const coords = utils.getEventCoords(e);
                const relativeX = coords.x - rect.left;
                const relativeY = coords.y - rect.top;

                const contentX = viewer.scrollLeft + relativeX;
                const contentY = viewer.scrollTop + relativeY;
                
                const newZoom = 2;
                setMediaZoom(newZoom);
                
                const newContentX = contentX * newZoom;
                const newContentY = contentY * newZoom;

                viewer.scrollTo({{ 
                    left: newContentX - relativeX, 
                    top: newContentY - relativeY, 
                    behavior: 'smooth' 
                }});
            }}
            state.lastTapTime = 0; // Reset tap time to prevent triple tap zoom
        }} else {{
            state.lastTapTime = now;
        }}
    }}


    function updateMousePos(e) {{
      state.mouseX = e.clientX;
      state.mouseY = e.clientY;
    }}

    function updateMousePosTouch(e) {{
      if (e.touches.length > 0) {{
        state.mouseX = e.touches[0].clientX;
        state.mouseY = e.touches[0].clientY;
      }}
    }}

    function startAutoScroll() {{
      if (state.autoScrollActive) return;
      state.autoScrollActive = true;
      autoScrollLoop();
    }}

    function stopAutoScroll() {{
      state.autoScrollActive = false;
    }}

    function autoScrollLoop() {{
      if (!state.autoScrollActive) return;
      
      const viewer = elements.mediaViewer;
      const rect = viewer.getBoundingClientRect();
      const edgeSize = 50;
      const scrollSpeed = 10;
      
      let dx = 0, dy = 0;
      
      if (state.mouseX < rect.left + edgeSize) {{
        dx = -scrollSpeed * ((rect.left + edgeSize - state.mouseX) / edgeSize);
      }} else if (state.mouseX > rect.right - edgeSize) {{
        dx = scrollSpeed * ((state.mouseX - (rect.right - edgeSize)) / edgeSize);
      }}
      
      if (state.mouseY < rect.top + edgeSize) {{
        dy = -scrollSpeed * ((rect.top + edgeSize - state.mouseY) / edgeSize);
      }} else if (state.mouseY > rect.bottom - edgeSize) {{
        dy = scrollSpeed * ((state.mouseY - (rect.bottom - edgeSize)) / edgeSize);
      }}
      
      if (dx !== 0 || dy !== 0) {{
        viewer.scrollLeft += dx;
        viewer.scrollTop += dy;
        
        if (state.isDragging || state.isResizing) {{
           state.startMouseX -= dx;
           state.startMouseY -= dy;
        
           const fakeEvent = {{ clientX: state.mouseX, clientY: state.mouseY, preventDefault: () => {{}} }}; 
           if (state.isDragging) {{
               dragHandlers.move(fakeEvent);
           }} else if (state.isResizing) {{
               resizeHandlers.move(fakeEvent);
           }}
        }}
      }}
      
      requestAnimationFrame(autoScrollLoop);
    }}


    function handleKeyboard(e) {{
      if (state.isHelpVisible && e.key === 'Escape') {{
        toggleHelp();
        return;
      }}
      
      if(elements.floatingPreview.classList.contains('fullscreen') && e.key === 'Escape') {{
          closePreviewFullscreen();
          return;
      }}
      
      if (e.target.tagName === 'INPUT') return;
      
      if (state.isHelpVisible || state.mediaType === 'audio' || !elements.crop) return;
      
      const step = e.shiftKey ? 1 : 10;
      const currentLeft = parseFloat(elements.crop.style.left) || 0;
      const currentTop = parseFloat(elements.crop.style.top) || 0;
      const currentWidth = parseFloat(elements.crop.style.width) || 0;
      const currentHeight = parseFloat(elements.crop.style.height) || 0;
      
      let newLeft = currentLeft;
      let newTop = currentTop;
      
      switch (e.key) {{
        case 'ArrowLeft':
          e.preventDefault();
          newLeft = Math.max(0, currentLeft - step);
          break;
        case 'ArrowRight':
          e.preventDefault();
          newLeft = Math.min(state.mediaWidth - currentWidth, currentLeft + step);
          break;
        case 'ArrowUp':
          e.preventDefault();
          newTop = Math.max(0, currentTop - step);
          break;
        case 'ArrowDown':
          e.preventDefault();
          newTop = Math.min(state.mediaHeight - currentHeight, currentTop + step);
          break;
        case 'c': case 'C':
          e.preventDefault(); centerCrop(); break;
        case 'g': case 'G':
          e.preventDefault(); toggleGrid(); break;
        case 'Enter':
          if (document.activeElement === elements.crop) {{
            e.preventDefault(); 
            saveCrop();
          }}
          break;
        default: return;
      }}
      
      if (newLeft !== currentLeft || newTop !== currentTop) {{
        setCropDimensions(newLeft, newTop, currentWidth, currentHeight, true);
        
        const viewer = elements.mediaViewer;
        const cropRect = elements.crop.getBoundingClientRect();
        const viewerRect = viewer.getBoundingClientRect();
        
        const scrollMargin = 50;
        
        if (cropRect.left < viewerRect.left + scrollMargin && viewer.scrollLeft > 0) {{
            viewer.scrollLeft -= step * 2;
        }} else if (cropRect.right > viewerRect.right - scrollMargin && viewer.scrollLeft < viewer.scrollWidth - viewer.clientWidth) {{
            viewer.scrollLeft += step * 2;
        }}
        
        if (cropRect.top < viewerRect.top + scrollMargin && viewer.scrollTop > 0) {{
            viewer.scrollTop -= step * 2;
        }} else if (cropRect.bottom > viewerRect.bottom - scrollMargin && viewer.scrollTop < viewer.scrollHeight - viewer.clientHeight) {{
            viewer.scrollTop += step * 2;
        }}
      }}
    }}

    function toggleGrid() {{
      state.showGrid = !state.showGrid;
      if(elements.crop) elements.crop.classList.toggle('show-grid', state.showGrid);
    }}

    function centerCrop() {{
      if (state.mediaType === 'audio' || !elements.crop) return;
      
      const currentWidth = parseFloat(elements.crop.style.width) || 0;
      const currentHeight = parseFloat(elements.crop.style.height) || 0;
      
      const centerX = (state.mediaWidth - currentWidth) / 2;
      const centerY = (state.mediaHeight - currentHeight) / 2;
      
      setCropDimensions(centerX, centerY, currentWidth, currentHeight, true);

      const viewer = elements.mediaViewer;
      const targetScrollLeft = centerX + currentWidth / 2 - viewer.clientWidth / 2;
      const targetScrollTop = centerY + currentHeight / 2 - viewer.clientHeight / 2;
      
      viewer.scrollTo({{
          left: targetScrollLeft,
          top: targetScrollTop,
          behavior: 'smooth' 
      }});
    }}

    function resetCropSize() {{
      if (state.mediaType === 'audio' || !elements.crop) return;
      
      // Clear saved state from localStorage
      const key = getStorageKey();
      if (key) localStorage.removeItem(key);
      
      setMediaZoom(1);
      positionCropBox(); 
      elements.aspectSelect.value = "free";
      state.aspectMode = "free";
      state.aspectRatio = null;
      elements.customRatio.classList.remove('visible');
      
      elements.keepAspect.checked = true;
      state.keepAspect = true;
    }}

    function toggleHelp() {{
      state.isHelpVisible = !state.isHelpVisible;
      elements.helpModal.style.display = state.isHelpVisible ? 'flex' : 'none';
      if (!state.isHelpVisible && elements.crop) {{
        elements.crop.focus(); 
      }}
    }}

    function showContextMenu(e) {{
      if (state.mediaType === 'audio' || !elements.crop) return;
      e.preventDefault();
      const menu = elements.contextMenu;
      menu.style.display = 'block';
      
      const menuWidth = menu.offsetWidth;
      const menuHeight = menu.offsetHeight;
      const viewportWidth = window.innerWidth;
      const viewportHeight = window.innerHeight;
      
      let left = e.clientX;
      let top = e.clientY;
      
      if (left + menuWidth > viewportWidth - 10) {{
          left = viewportWidth - menuWidth - 10;
      }}
      if (top + menuHeight > viewportHeight - 10) {{
          top = viewportHeight - menuHeight - 10;
      }}
      left = Math.max(10, left);
      top = Math.max(10, top); 
      
      menu.style.left = left + 'px';
      menu.style.top = top + 'px';
      
      document.addEventListener('click', hideContextMenu, {{ once: true, capture: true }});
    }}

    function hideContextMenu(e) {{
      if (elements.contextMenu && elements.contextMenu.contains(e?.target)) {{
           if (!e?.target.classList.contains('context-item')) {{
               document.addEventListener('click', hideContextMenu, {{ once: true, capture: true }});
           }}
           return; 
      }}
      if (elements.contextMenu) {{
        elements.contextMenu.style.display = 'none';
      }}
    }}

     function handleAspectRatioChange(e) {{
      state.aspectMode = e.target.value;
      
      if (state.aspectMode === "custom") {{
        elements.customRatio.classList.add('visible');
        updateCustomAspectRatio();
      }} else {{
        elements.customRatio.classList.remove('visible');
        
        if (state.aspectMode === "free") {{
          state.aspectRatio = null;
        }} else {{ 
            if (state.aspectMode === "original") {{
              if (state.naturalWidth && state.naturalHeight && state.naturalHeight !== 0) {{
                state.aspectRatio = state.naturalWidth / state.naturalHeight;
              }} else {{
                state.aspectRatio = null;
              }}
            }} else {{
              const parts = state.aspectMode.split(":");
              if (parts.length === 2 && parseFloat(parts[1]) !== 0) {{
                 state.aspectRatio = parseFloat(parts[0]) / parseFloat(parts[1]);
              }} else {{
                 state.aspectRatio = null;
              }}
            }}
            
            // --- IMPROVEMENT: Haptic Feedback ---
            utils.vibrate(10);
            
            if (state.keepAspect) {{
                applyCurrentAspectRatio();
            }}
        }}
      }}
      updateCropInfo(); 
    }}

    function updateCustomAspectRatio() {{
      const w = parseFloat(elements.customW.value);
      const h = parseFloat(elements.customH.value);
      
      if (!isNaN(w) && !isNaN(h) && h !== 0 && w > 0 && h > 0) {{
          state.aspectRatio = w / h;
          if (state.aspectMode === "custom" && state.keepAspect) {{
            applyCurrentAspectRatio();
          }}
      }} else {{
          state.aspectRatio = null;
      }}
      updateCropInfo();
    }}

    function applyCurrentAspectRatio() {{
      if (!state.aspectRatio || !state.isInitialized || state.mediaType === 'audio' || !elements.crop) return;
      
      const currentLeft = parseFloat(elements.crop.style.left) || 0;
      const currentTop = parseFloat(elements.crop.style.top) || 0;
      const currentWidth = parseFloat(elements.crop.style.width) || 0;
      const currentHeight = parseFloat(elements.crop.style.height) || 0;

      let newWidth = currentWidth;
      let newHeight = Math.round(currentWidth / state.aspectRatio);

      if (newHeight < 30 || newHeight > state.mediaHeight) {{
          newHeight = currentHeight;
          newWidth = Math.round(currentHeight * state.aspectRatio);
      }}
        
      setCropDimensions(currentLeft, currentTop, newWidth, newHeight, true);
    }}

    function saveCrop() {{
      if (state.mediaType === 'audio' || !elements.crop) {{
        alert("Crop function is not applicable for this media type.");
        return;
      }}
      
      updateMediaDimensions();
      
      const finalX = parseInt(elements.actualX.value) || 0;
      const finalY = parseInt(elements.actualY.value) || 0;
      const finalW = parseInt(elements.actualW.value) || 0;
      const finalH = parseInt(elements.actualH.value) || 0;
      
      if (finalW <= 0 || finalH <= 0) {{
          alert("Invalid crop dimensions (Width and Height must be positive).");
          return;
      }}
       if (finalX < 0 || finalY < 0) {{
           alert("Invalid crop position (X and Y cannot be negative).");
           return;
       }}
       if (state.naturalWidth && state.naturalHeight) {{
           if (finalX + finalW > state.naturalWidth || finalY + finalH > state.naturalHeight) {{
               console.warn("Calculated crop exceeds natural media dimensions. Clamping might occur in FFmpeg.");
           }}
       }}

      fetch("/save", {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify({{ 
          x: finalX, y: finalY, w: finalW, h: finalH,
          mediaType: state.mediaType
        }})
      }})
      .then(response => {{
        if (response.ok) {{
          return response.json();
        }} else {{
          return response.json().then(data => {{
              throw new Error(data.message || `Server responded with status: ${{response.status}}`);
          }}).catch(() => {{
              throw new Error(`Server responded with status: ${{response.status}}`);
          }});
        }}
      }})
      .then(data => {{
          console.log("Save successful:", data);
          const notification = document.createElement('div');
          notification.className = 'notification';
          notification.innerHTML = `
            <div class="notification-title">Crop Saved Successfully!</div>
            <div class="notification-code">${{data.crop_filter || `crop=${{finalW}}:${{finalH}}:${{finalX}}:${{finalY}}`}}</div>
            <div class="notification-subtitle">Crop filter string printed to terminal.</div>
          `;
          document.body.appendChild(notification);
          setTimeout(() => {{
              if (document.body.contains(notification)) {{
                  document.body.removeChild(notification);
              }}
          }}, 3000);
      }})
      .catch(error => {{
        console.error("Save failed:", error);
        alert("Error saving crop parameters: " + error.message);
      }});
    }}

    const handleWindowResize = utils.debounce(() => {{
      if (!state.isInitialized) return;
      
      const currentActualW = parseInt(elements.actualW.value) || 0;
      const currentActualH = parseInt(elements.actualH.value) || 0;
      const currentActualX = parseInt(elements.actualX.value) || 0;
      const currentActualY = parseInt(elements.actualY.value) || 0;
      
      updateMediaDimensions();
      
      if (state.naturalWidth && state.naturalHeight && state.mediaWidth && state.mediaHeight) {{
          const scaleX = state.naturalWidth / state.mediaWidth;
          const scaleY = state.naturalHeight / state.mediaHeight;
          if (scaleX > 0 && scaleY > 0) {{
            const newPreviewW = Math.round(currentActualW / scaleX);
            const newPreviewH = Math.round(currentActualH / scaleY);
            const newPreviewX = Math.round(currentActualX / scaleX);
            const newPreviewY = Math.round(currentActualY / scaleY);
            setCropDimensions(newPreviewX, newPreviewY, newPreviewW, newPreviewH); 
          }} else {{
              positionCropBox();
          }}
      }} else {{
          positionCropBox();
      }}

    }}, 200);


    function openPreviewFullscreen() {{
        if (!elements.floatingPreview.classList.contains('fullscreen')) {{
            elements.floatingPreview.classList.add('fullscreen');
        }}
    }}
    
    function closePreviewFullscreen() {{
        if (elements.floatingPreview.classList.contains('fullscreen')) {{
            elements.floatingPreview.classList.remove('fullscreen');
        }}
    }}
    
    const previewInteraction = {{
        isDragging: false,
        hasDragged: false,
        dragStartX: 0, dragStartY: 0,
        previewStartX: 0, previewStartY: 0,
        
        onMouseDown(e) {{
            if (e.button !== 0 && e.type === 'mousedown') return; 
            
            e.preventDefault(); 
            this.isDragging = true;
            this.hasDragged = false; 
            const coords = utils.getEventCoords(e);
            this.dragStartX = coords.x;
            this.dragStartY = coords.y;
            
            const rect = elements.floatingPreview.getBoundingClientRect();
            this.previewStartX = rect.left;
            this.previewStartY = rect.top;

            elements.floatingPreview.style.left = this.previewStartX + 'px';
            elements.floatingPreview.style.top = this.previewStartY + 'px';
            elements.floatingPreview.style.right = 'auto';
            elements.floatingPreview.style.bottom = 'auto';
            elements.floatingPreview.style.transition = 'none'; 

            document.addEventListener('mousemove', this.onMouseMove);
            document.addEventListener('mouseup', this.onMouseUp);
            document.addEventListener('touchmove', this.onMouseMove, {{ passive: false }});
            document.addEventListener('touchend', this.onMouseUp);
        }},

        onMouseMove(e) {{
            if (!previewInteraction.isDragging) return;
            
            if (e.type === 'touchmove') e.preventDefault(); 
            
            const coords = utils.getEventCoords(e);
            const dx = coords.x - previewInteraction.dragStartX;
            const dy = coords.y - previewInteraction.dragStartY;
            
            if (!previewInteraction.hasDragged && Math.hypot(dx, dy) > 5) {{
                previewInteraction.hasDragged = true;
                if(state.holdTimer) clearTimeout(state.holdTimer);
            }}

            let newLeft = previewInteraction.previewStartX + dx;
            let newTop = previewInteraction.previewStartY + dy;
            
            const previewWidth = elements.floatingPreview.offsetWidth;
            const previewHeight = elements.floatingPreview.offsetHeight;
            newLeft = Math.max(0, Math.min(newLeft, window.innerWidth - previewWidth));
            newTop = Math.max(0, Math.min(newTop, window.innerHeight - previewHeight));
            
            elements.floatingPreview.style.left = newLeft + 'px';
            elements.floatingPreview.style.top = newTop + 'px';
        }},

        onMouseUp() {{
            if (!this.isDragging) return;
            this.isDragging = false;
            elements.floatingPreview.style.transition = '';
            
            document.removeEventListener('mousemove', this.onMouseMove);
            document.removeEventListener('mouseup', this.onMouseUp);
            document.removeEventListener('touchmove', this.onMouseMove);
            document.removeEventListener('touchend', this.onMouseUp);
        }},

        onContentMouseDown(e) {{
            if (e.button !== 0 && e.type === 'mousedown') return;
            if (e.touches && e.touches.length > 1) return; 
            
            if (e.target.classList.contains('preview-resize-handle')) return;
            
             if(state.holdTimer) clearTimeout(state.holdTimer);
             
            this.hasDragged = false;
            
            state.holdTimer = setTimeout(() => {{
                if (!this.hasDragged) {{ 
                    openPreviewFullscreen();
                }}
            }}, 700);
        }},
        
        onContentMouseUp(e) {{
            if(state.holdTimer) clearTimeout(state.holdTimer);
            
            if (!this.hasDragged && e.type !== 'touchend') {{ 
            }}
            this.hasDragged = false; 
        }},
        
        bind(element, handler) {{
            return handler.bind(element);
        }}
    }};
    previewInteraction.onMouseDown = previewInteraction.bind(previewInteraction, previewInteraction.onMouseDown);
    previewInteraction.onMouseMove = previewInteraction.bind(previewInteraction, previewInteraction.onMouseMove);
    previewInteraction.onMouseUp = previewInteraction.bind(previewInteraction, previewInteraction.onMouseUp);
    previewInteraction.onContentMouseDown = previewInteraction.bind(previewInteraction, previewInteraction.onContentMouseDown);
    previewInteraction.onContentMouseUp = previewInteraction.bind(previewInteraction, previewInteraction.onContentMouseUp);
    
    const previewResizeHandlers = {{
        start(e) {{
            if (e.button !== 0 && e.type === 'mousedown') return;
            
            e.preventDefault();
            e.stopPropagation();
            if(state.holdTimer) clearTimeout(state.holdTimer);

            state.isResizingPreview = true;
            state.resizeDirection = Array.from(e.target.classList).find(cls => cls.startsWith('p-'));
            const coords = utils.getEventCoords(e);
            state.startMouseX = coords.x;
            state.startMouseY = coords.y;
            
            const rect = elements.floatingPreview.getBoundingClientRect();
            state.startCropLeft = rect.left;
            state.startCropTop = rect.top;
            state.startCropWidth = rect.width;
            state.startCropHeight = rect.height;

            elements.floatingPreview.style.transition = 'none';
            elements.floatingPreview.style.left = state.startCropLeft + 'px';
            elements.floatingPreview.style.top = state.startCropTop + 'px';
            elements.floatingPreview.style.right = 'auto';
            elements.floatingPreview.style.bottom = 'auto';

            document.addEventListener('mousemove', this.move, {{ passive: false }});
            document.addEventListener('mouseup', this.stop, {{ once: true }});
            document.addEventListener('touchmove', this.move, {{ passive: false }});
            document.addEventListener('touchend', this.stop, {{ once: true }});
        }},
        
        move(e) {{
            if (!state.isResizingPreview) return;
            
            if (e.type === 'touchmove') e.preventDefault();
            
            const coords = utils.getEventCoords(e);
            const deltaX = coords.x - state.startMouseX;
            const deltaY = coords.y - state.startMouseY;

            let newLeft = state.startCropLeft;
            let newTop = state.startCropTop;
            let newWidth = state.startCropWidth;
            let newHeight = state.startCropHeight;
            const direction = state.resizeDirection;

            if (direction.includes('e')) newWidth = state.startCropWidth + deltaX;
            if (direction.includes('w')) newWidth = state.startCropWidth - deltaX;
            if (direction.includes('s')) newHeight = state.startCropHeight + deltaY;
            if (direction.includes('n')) newHeight = state.startCropHeight - deltaY;

            const minWidth = 150, minHeight = 120;
            if (newWidth < minWidth) newWidth = minWidth;
            if (newHeight < minHeight) newHeight = minHeight;
            
            if (direction.includes('w')) newLeft = state.startCropLeft + (state.startCropWidth - newWidth);
            if (direction.includes('n')) newTop = state.startCropTop + (state.startCropHeight - newHeight);
           
            elements.floatingPreview.style.left = newLeft + 'px';
            elements.floatingPreview.style.top = newTop + 'px';
            elements.floatingPreview.style.width = newWidth + 'px';
            elements.floatingPreview.style.height = newHeight + 'px';
        }},
        
        stop() {{
            if (!state.isResizingPreview) return;
            state.isResizingPreview = false;
            elements.floatingPreview.style.transition = '';
            
            document.removeEventListener('mousemove', this.move);
            document.removeEventListener('touchmove', this.move);
        }}
    }};
    previewResizeHandlers.start = previewResizeHandlers.start.bind(previewResizeHandlers);
    previewResizeHandlers.move = previewResizeHandlers.move.bind(previewResizeHandlers);
    previewResizeHandlers.stop = previewResizeHandlers.stop.bind(previewResizeHandlers);
    
    function startPreviewPinch(e) {{
        if (!e.touches || e.touches.length !== 2) return;
        e.preventDefault();
        e.stopPropagation(); 

        if(state.holdTimer) clearTimeout(state.holdTimer);

        state.isPreviewPinching = true;
        state.previewPinchInitialDist = utils.getDistance(e.touches[0], e.touches[1]);
        if (state.previewPinchInitialDist === 0) {{
             state.isPreviewPinching = false;
             return;
        }}

        const rect = elements.floatingPreview.getBoundingClientRect();
        state.previewPinchInitialWidth = rect.width;
        state.previewPinchInitialHeight = rect.height;

        elements.floatingPreview.style.transition = 'none';

        document.addEventListener('touchmove', handlePreviewPinchMove, {{ passive: false }});
        document.addEventListener('touchend', handlePreviewPinchEnd, {{ once: true }}); 
    }}

    function handlePreviewPinchMove(e) {{
        if (!state.isPreviewPinching || !e.touches || e.touches.length !== 2) return;
        e.preventDefault();

        const newDist = utils.getDistance(e.touches[0], e.touches[1]);
        const factor = newDist / state.previewPinchInitialDist;

        let newWidth = state.previewPinchInitialWidth * factor;
        let newHeight = state.previewPinchInitialHeight * factor;

        const minWidth = 150;
        const minHeight = 120;
        const maxWidth = window.innerWidth * 0.95;
        const maxHeight = window.innerHeight * 0.95;

        newWidth = Math.max(minWidth, Math.min(newWidth, maxWidth));
        newHeight = Math.max(minHeight, Math.min(newHeight, maxHeight));

        elements.floatingPreview.style.width = newWidth + 'px';
        elements.floatingPreview.style.height = newHeight + 'px';
    }}

    function handlePreviewPinchEnd() {{
        if (!state.isPreviewPinching) return;
        state.isPreviewPinching = false;
        elements.floatingPreview.style.transition = '';
        document.removeEventListener('touchmove', handlePreviewPinchMove); 
    }}
    
    // --- IMPROVEMENT: Label Drag Handlers ---
    const labelDragHandler = {{
        start(e, inputElement) {{
            e.preventDefault();
            e.stopPropagation();
            
            if (!inputElement) return;

            state.isLabelDragging = true;
            state.labelDragInput = inputElement;
            state.labelDragStartX = e.clientX;
            state.labelDragInitialValue = parseFloat(inputElement.value) || 0;
            
            document.body.style.cursor = 'ew-resize';
            
            document.addEventListener('mousemove', this.move, {{ passive: false }});
            document.addEventListener('mouseup', this.stop, {{ once: true }});
            document.addEventListener('touchmove', this.move, {{ passive: false }});
            document.addEventListener('touchend', this.stop, {{ once: true }});
        }},
        
        move: utils.throttle((e) => {{
            if (!state.isLabelDragging || !state.labelDragInput) return;
            e.preventDefault();
            
            const coords = utils.getEventCoords(e);
            const deltaX = coords.x - state.labelDragStartX;

            const step = e.shiftKey ? 0.1 : 1;
            const newValue = state.labelDragInitialValue + Math.round(deltaX * step);

            state.labelDragInput.value = newValue;
            
            state.labelDragInput.dispatchEvent(new Event('change'));
            
        }}, 32),
        
        stop() {{
            state.isLabelDragging = false;
            state.labelDragInput = null;
            document.body.style.cursor = 'default';
            
            document.removeEventListener('mousemove', this.move);
            document.removeEventListener('mouseup', this.stop);
            document.removeEventListener('touchmove', this.move);
            document.removeEventListener('touchend', this.stop);
        }}
    }};

    labelDragHandler.start = labelDragHandler.start.bind(labelDragHandler);
    labelDragHandler.move = labelDragHandler.move.bind(labelDragHandler);
    labelDragHandler.stop = labelDragHandler.stop.bind(labelDragHandler);


    function setupEventListeners() {{
      elements.themeToggle.addEventListener("click", toggleTheme);
      
      if (elements.crop) {{
        elements.crop.addEventListener("mousedown", dragHandlers.start);
        elements.crop.addEventListener("touchstart", dragHandlers.start, {{ passive: false }});
        elements.crop.addEventListener("contextmenu", showContextMenu);
        elements.crop.addEventListener("dblclick", centerCrop);
      
        document.querySelectorAll('.resize-handle').forEach(handle => {{
          handle.addEventListener("mousedown", resizeHandlers.start);
          handle.addEventListener("touchstart", resizeHandlers.start, {{ passive: false }});
        }});
      }}
      
      if (elements.mediaWrapper) {{
          elements.mediaWrapper.addEventListener("touchstart", handleMediaTouchStart, {{ passive: false }});

          elements.mediaWrapper.addEventListener("touchend", handleDoubleTap, {{ passive: false }});
      }}
      
      if (elements.mediaViewer) {{
          elements.mediaViewer.style.cursor = 'grab'; // Initial cursor for panning
          elements.mediaViewer.addEventListener("wheel", handleMouseWheelZoom, {{ passive: false }});

          elements.mediaViewer.addEventListener("mousedown", panHandlers.start, {{ passive: false }});
          // Touch pan is handled by handleMediaTouchStart
      }}
      
      elements.aspectSelect.addEventListener("change", handleAspectRatioChange);
      elements.customW.addEventListener("input", utils.debounce(updateCustomAspectRatio, 300));
      elements.customH.addEventListener("input", utils.debounce(updateCustomAspectRatio, 300));
      
      elements.keepAspect.addEventListener('change', (e) => {{
          state.keepAspect = e.target.checked;
          if (state.keepAspect) {{
              applyCurrentAspectRatio();
          }}
      }});
      
      document.addEventListener("keydown", handleKeyboard);
      
      window.addEventListener("resize", handleWindowResize);
      
      document.addEventListener("selectstart", e => {{
        if (state.isDragging || state.isResizing || state.isResizingPreview || previewInteraction.isDragging || state.isPreviewPinching || state.isPanning || state.isLabelDragging) {{
            e.preventDefault();
        }}
      }});
      
      elements.helpModal.addEventListener('click', (e) => {{
        if (e.target === elements.helpModal) {{ 
          toggleHelp();
        }}
      }});
      
      if (elements.floatingPreview) {{
        elements.previewHeader.addEventListener('mousedown', previewInteraction.onMouseDown);
        elements.previewHeader.addEventListener('touchstart', previewInteraction.onMouseDown, {{ passive: false }});
        
        const previewContentTouchStart = (e) => {{
            if (e.touches.length === 2) {{
                startPreviewPinch(e); 
            }} else if (e.touches.length === 1) {{
                previewInteraction.onContentMouseDown(e);
            }}
        }};

        elements.previewCanvasWrapper.addEventListener('mousedown', previewInteraction.onContentMouseDown);
        elements.previewCanvasWrapper.addEventListener('mouseup', previewInteraction.onContentMouseUp);
        elements.previewCanvasWrapper.addEventListener('touchstart', previewContentTouchStart, {{ passive: false }});
        elements.previewCanvasWrapper.addEventListener('touchend', previewInteraction.onContentMouseUp);

        document.querySelectorAll('.preview-resize-handle').forEach(handle => {{
            handle.addEventListener('mousedown', previewResizeHandlers.start);
            handle.addEventListener('touchstart', previewResizeHandlers.start, {{ passive: false }});
        }});
        
        elements.previewCloseBtn.addEventListener('click', closePreviewFullscreen);
      }}

      // Input change listeners
      elements.previewX.addEventListener('change', handlePreviewInputChange);
      elements.previewY.addEventListener('change', handlePreviewInputChange);
      elements.previewW.addEventListener('change', handlePreviewInputChange);
      elements.previewH.addEventListener('change', handlePreviewInputChange);

      elements.actualX.addEventListener('change', handleActualInputChange);
      elements.actualY.addEventListener('change', handleActualInputChange);
      elements.actualW.addEventListener('change', handleActualInputChange);
      elements.actualH.addEventListener('change', handleActualInputChange);

      const inputs = [
          elements.previewX, elements.previewY, elements.previewW, elements.previewH,
          elements.actualX, elements.actualY, elements.actualW, elements.actualH,
          elements.customW, elements.customH
      ];
      
      inputs.forEach(input => {{

          input.addEventListener('keydown', (e) => {{
              if (e.key === 'Enter') {{
                  e.preventDefault();
                  e.target.blur();
              }}
          }});

          const label = input.previousElementSibling;
          if (label && label.classList.contains('info-input-label')) {{
              label.style.cursor = 'ew-resize';
              label.addEventListener('mousedown', (e) => labelDragHandler.start(e, input));
          }}
      }});
    }}

    document.addEventListener("DOMContentLoaded", function() {{
      initializeTheme();
      setupEventListeners();
      
      if (elements.media) {{
          if ((elements.media.readyState >= 1 && (media_type === 'video' || media_type === 'audio')) || (elements.media.complete && media_type === 'image')) {{
             console.log("Media already loaded or has metadata.");
             initializeCrop();
          }} else {{
              console.log("Media not loaded yet, adding listeners.");
              if (media_type === 'video' || media_type === 'audio') {{
                  elements.media.addEventListener('loadedmetadata', initializeCrop, {{ once: true }});
              }}
              if (media_type === 'image') {{
                 elements.media.addEventListener('load', initializeCrop, {{ once: true }});
              }}
              elements.media.addEventListener('canplay', initializeCrop, {{ once: true }});
              elements.media.addEventListener('error', () => {{
                console.error("Media failed to load.");
                const errorElement = document.getElementById('unsupported') || elements.mediaWrapper;
                if (errorElement) {{
                    errorElement.innerHTML = '<div class="unsupported-content"><div class="unsupported-icon">⚠️</div><div class="unsupported-text">Error Loading Media</div><div class="unsupported-subtext">The file might be corrupt or inaccessible.</div></div>';
                    elements.container.style.width = '500px'; 
                    elements.container.style.height = '300px';
                }}
                hideLoading();
              }}, {{ once: true }});
          }}
      }} else if (media_type === 'unsupported') {{
          console.log("Unsupported media type, initializing with default box.");
          setTimeout(initializeCrop, 50); 
      }} else {{
         console.error("Media element not found and type is not 'unsupported'.");
         hideLoading();
      }}
    }});
    """
    return js_code