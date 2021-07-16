#lang racket

; Metacircular evaluator
;
; In this file, we will implement the meta-circular evaluator as described
; in Section 4.1 of SICP.
;
; However, rather than literally following the book letter-for-letter, we
; will be making various changes and simplifications that allow us to
; make more incremental process.
;
; The evaluator consists of two core functions.
;
;    (seval ...)
;    (sapply ...)
;
; seval evaluates an expression and returns the result.
; sapply is used to apply a procedure to arguments.
;
; Big idea:  All of computation is expressed by combinations of eval and apply.
; Thus, these two procedures are what we'll work with.  

;; Environments

(define (make-environment)
  (make-hash))

(define (lookup-environment environ name)
  (hash-ref environ name))

(define (define-in-environment environ name value)
  (hash-set! environ name value))

(define globalenv (make-environment))
(define-in-environment globalenv '+ +)
(define-in-environment globalenv '* *)
(define-in-environment globalenv '/ /)
(define-in-environment globalenv '- -)
(define-in-environment globalenv '= =)
(define-in-environment globalenv 'x 5)



;; Eval/Apply

(define (seval exp environ)
    (cond [(primitive? exp) exp]
          [(symbol? exp)
           (lookup-environment environ exp)]
          [(if-exp? exp)
           (seval-if-statement exp environ)]
          [(list? exp)
           (sapply (car exp) (cdr exp) environ)]
          [else (error "Bad expression" exp)])
)

(define (sapply proc arguments environ)
    (let [(eproc (seval proc environ))
          (earguments (map
                       (λ (arg) (seval arg environ))
                       arguments))]
      (apply eproc earguments)))


(define (primitive? exp)
  (or (number? exp)
      (boolean? exp)))

;; "If" special form
(define (if-exp? exp)
  (and (list? exp)
       (= (length exp) 4)
       (eq? (car exp) 'if)))

(define (test if-exp)
  (cadr if-exp))

(define (true-branch if-exp)
  (caddr if-exp))

(define (else-branch if-exp)
  (cadddr if-exp))

(define (seval-if-statement if-exp environ)
    (if (seval (test if-exp) environ)
        (seval (true-branch if-exp) environ)
        (seval (else-branch if-exp) environ)))

