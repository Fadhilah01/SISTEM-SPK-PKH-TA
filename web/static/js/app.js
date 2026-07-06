/**
 * SPK PKH - App Shell: Sidebar Toggle, Password Toggle, Delete Modal, Custom Select Dropdowns
 *
 * Handles responsive sidebar drawer behavior, password visibility toggles,
 * Bootstrap modal interactions, and global declarative custom select dropdowns.
 */

document.addEventListener('DOMContentLoaded', function () {
    initSidebar();
    initPasswordToggles();
    initDeleteModal();
    initGlobalCustomSelects();
});

function initSidebar() {
    const toggleBtn = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebarPanel');
    const overlay = document.getElementById('sidebarOverlay');
    const closeBtn = document.getElementById('sidebarClose');

    if (!sidebar) return; // No sidebar on this page

    if (toggleBtn && overlay) {
        toggleBtn.addEventListener('click', function () {
            sidebar.classList.add('show');
            overlay.classList.add('show');
        });

        var closeSidebar = function () {
            sidebar.classList.remove('show');
            overlay.classList.remove('show');
        };

        overlay.addEventListener('click', closeSidebar);
        if (closeBtn) {
            closeBtn.addEventListener('click', closeSidebar);
        }
    }
}

/**
 * Password Visibility Toggle
 * Adds click-to-toggle behavior on .password-toggle buttons.
 * Button must have data-target="elementId" pointing to the password input.
 */
function initPasswordToggles() {
    document.querySelectorAll('.password-toggle').forEach(function (btn) {
        btn.addEventListener('click', function () {
            const input = document.getElementById(this.dataset.target);
            const icon = this.querySelector('i');
            if (!input) return;

            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.replace('bi-eye', 'bi-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.replace('bi-eye-slash', 'bi-eye');
            }
        });
    });
}

/**
 * Delete Confirmation Modal
 * Handles the #hapusModal Bootstrap modal: sets form action and body text
 * from the triggering button's data-id and data-nama attributes.
 */
function initDeleteModal() {
    const modal = document.getElementById('hapusModal');
    if (!modal) return;

    modal.addEventListener('show.bs.modal', function (event) {
        const btn = event.relatedTarget;
        if (!btn) return;

        const id = btn.dataset.id;
        const nama = btn.dataset.nama;

        const bodyEl = modal.querySelector('#hapusModalBody');
        const formEl = modal.querySelector('#hapusForm');

        if (bodyEl) {
            bodyEl.textContent = 'Hapus akses admin untuk ' + nama + '? Tindakan ini tidak dapat dibatalkan.';
        }
        if (formEl) {
            formEl.action = '/admin/users/' + id + '/hapus';
        }
    });
}

/**
 * Global Custom Select Dropdowns
 * Declaratively transforms any .custom-select elements into searchable,
 * styled monochrome selects that sync automatically with hidden inputs.
 */
function initGlobalCustomSelects() {
    document.querySelectorAll(".custom-select").forEach(el => {
        if (el.dataset.customSelectInitialized) return;

        const button = el.querySelector(".form-select");
        const searchInput = el.querySelector(".select-search-input");
        const listContainer = el.querySelector(".select-items-list");
        const hiddenInput = el.querySelector("input[type='hidden']");

        if (!button || !listContainer) return;

        const placeholder = button.textContent.trim();

        // Track selected value
        el.value = hiddenInput ? hiddenInput.value : "";
        el.kode = "";

        function selectItem(itemEl, triggerChange = true) {
            listContainer.querySelectorAll(".select-item").forEach(x => x.classList.remove("active"));
            itemEl.classList.add("active");

            const val = itemEl.dataset.value || "";
            const kode = itemEl.dataset.kode || "";
            
            el.value = val;
            el.kode = kode;
            button.textContent = itemEl.textContent.trim();

            if (hiddenInput) {
                hiddenInput.value = val;
                hiddenInput.dispatchEvent(new Event("change", { bubbles: true }));
            }

            if (triggerChange) {
                el.dispatchEvent(new CustomEvent("change", { 
                    bubbles: true, 
                    detail: { value: val, kode: kode } 
                }));
            }
        }

        // Bind existing static items (pre-rendered in templates)
        function bindItems() {
            listContainer.querySelectorAll(".select-item").forEach(item => {
                item.onclick = function() {
                    selectItem(item);
                };

                // Handle pre-selected values
                if (item.classList.contains("active")) {
                    selectItem(item, false);
                } else if (hiddenInput && item.dataset.value === hiddenInput.value) {
                    selectItem(item, false);
                }
            });
        }

        bindItems();

        // Search filter logic
        if (searchInput) {
            searchInput.addEventListener("input", function() {
                const query = searchInput.value.toLowerCase();
                listContainer.querySelectorAll(".select-item").forEach(item => {
                    const text = item.textContent.toLowerCase();
                    if (text.includes(query)) {
                        item.classList.remove("d-none");
                    } else {
                        item.classList.add("d-none");
                    }
                });
            });

            // Prevent dropdown closure when clicking/typing inside search field
            searchInput.addEventListener("click", function(e) {
                e.stopPropagation();
            });
        }

        // Set dynamic items programmatically (e.g. for regional selects)
        el.setItems = function(items, activeVal = "") {
            listContainer.innerHTML = `<button class="dropdown-item py-1 px-2 small select-item select-default-item" type="button" data-value="">${placeholder}</button>`;
            
            items.forEach(item => {
                const btn = document.createElement("button");
                btn.className = "dropdown-item py-1 px-2 small select-item text-truncate";
                btn.type = "button";
                btn.dataset.value = item.nama;
                btn.dataset.kode = item.kode;
                
                let displayText = item.nama;
                if (el.id === 'select_kabupaten') {
                    displayText = item.nama.replace("KABUPATEN ", "").replace("KOTA ", "");
                }
                btn.textContent = displayText;
                listContainer.appendChild(btn);
            });

            bindItems();

            if (searchInput) searchInput.value = "";

            if (activeVal) {
                const activeItem = Array.from(listContainer.querySelectorAll(".select-item")).find(x => x.dataset.value === activeVal);
                if (activeItem) {
                    selectItem(activeItem, false);
                }
            } else {
                const defaultItem = listContainer.querySelector(".select-default-item");
                selectItem(defaultItem, false);
            }
        };

        el.disable = function(disabled) {
            button.disabled = disabled;
            if (disabled) {
                el.value = "";
                el.kode = "";
                if (hiddenInput) hiddenInput.value = "";
                button.textContent = placeholder;
                listContainer.innerHTML = `<button class="dropdown-item py-1 px-2 small select-item select-default-item active" type="button" data-value="">${placeholder}</button>`;
            }
        };

        el.dataset.customSelectInitialized = "true";
    });
}
