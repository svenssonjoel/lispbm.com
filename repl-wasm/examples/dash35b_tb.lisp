
;; Testbench for: https://raw.githubusercontent.com/vedderb/vesc_pkg/refs/heads/main/dash35b/main.lisp

(import "/libs/vesc_stubs.lisp" 'vs)
(read-eval-program vs)

(def tab (wasm-create-tab "Dash35b"))
(def canvas (wasm-add-canvas tab 480 320))

(sleep 25)

(wasm-add-button tab '(
  ("Page"       "(on-btn-0-pressed)")
  ("Mode -"     "(on-btn-1-pressed)")
  ("Mode +"     "(on-btn-2-pressed)")
  ("Light"      "(on-btn-3-pressed)")
))

(def r (range 0 10))
(def soc (map (fn (x) (* x 0.1)) r))
(def kmh (map (fn (x) (* x 10)) r))
(def kw  (map (fn (x) (* x 20.0)) r))
(def vin (map (fn (x) (* x 10.0)) r))
              
(loopwhile t {
      (loopfor i 0 (< i 10) (+ i 1) {
            (setq stats-battery-soc (ix soc i))  
            (setq stats-kmh (ix kmh i))
            (setq stats-kw (ix kw i))
            (setq stats-vin (ix vin i))
            (sleep 0.5)
            })
      })
