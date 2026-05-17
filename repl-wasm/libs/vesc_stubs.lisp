; Stubs for VESC hardware functions not available in the WASM REPL.

(defun disp-set-bl (lvl) nil)
(defun disp-orientation (n) nil)

(defun can-send-sid (id data) nil)

(defun event-enable (sym) nil)

(defun connected-usb () nil)
(defun btn-pull-en (en) nil)

(defun i2c-tx-rx (addr tx-buf) nil)

(defun reboot () nil)

; Stubs for lib_code_server — CAN-based remote code execution not available in WASM REPL.

(defun mutex-create () nil)
(defun mutex-lock (mtx) nil)
(defun mutex-unlock (mtx) nil)

(defun start-code-server () nil)

(defun rcode-run (id tout code)
    (print "rcode-run: CAN not available in WASM REPL")
    'timeout
)

(defun rcode-run-noret (id code)
    (print "rcode-run-noret: CAN not available in WASM REPL")
    nil
)
