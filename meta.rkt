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

(define (make-environment enclosing-env)
  (cons (make-hash) enclosing-env))

(define (env-table env)
  (car env))

(define (env-parent env)
  (cdr env))

(define (lookup-environment environ name)
  (let [(lookup-result (safe-lookup-environment environ name))]
    (let [(success? (car lookup-result))
          (value (cadr lookup-result))]
      (if (not success?)
          (error "Name not found:" name)
          value))))

(define (safe-lookup-environment environ name)
  (if (null? environ)
      (list #false null environ)
      (let [(table (car environ))
            (parent (cdr environ))]
        (if (hash-has-key? table name)
            (list #true (hash-ref table name) environ)
            (safe-lookup-environment parent name)))))

(define (define-in-environment environ name value)
  (hash-set! (env-table environ) name value))

(define (set-in-environment environ name value)
  (let [(lookup-result (safe-lookup-environment environ name))]
    (let [(success? (car lookup-result))
          (found-in (caddr lookup-result))]
      (if (not success?)
          (error "Name not found:" name)
          (hash-set! (env-table found-in) name value)))))

(define globalenv (make-environment null))
(define-in-environment globalenv '+ +)
(define-in-environment globalenv '* *)
(define-in-environment globalenv '/ /)
(define-in-environment globalenv '- -)
(define-in-environment globalenv '= =)
(define-in-environment globalenv 'display display)
(define-in-environment globalenv 'newline newline)



;; Eval/Apply

(define (seval exp environ)
  (cond [(primitive? exp) exp]
        [(symbol? exp)
         (lookup-environment environ exp)]
        [(if-exp? exp)
         (seval-if-statement exp environ)]
        [(define-exp? exp)
         (seval-define exp environ)]
        [(begin-exp? exp)
         (seval-begin-exp exp environ)]
        [(lambda? exp)
         (seval-lambda exp environ)]
        [(set-exp? exp)
         (seval-set-exp exp environ)]
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

;; "if" special form
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

;; "define" special form (no function definition)
(define (define-exp? exp)
  (and (list? exp)
       (= (length exp) 3)
       (symbol? (cadr exp))
       (eq? (car exp) 'define)))

(define (define-name exp)
  (cadr exp))

(define (define-value-exp exp)
  (caddr exp))

(define (seval-define def-exp environ)
  (let [(name (define-name def-exp))]
    (let [(already-defined?
           (car (safe-lookup-environment environ name)))]
      (if already-defined?
          (error "Already defined:" name)
          (define-in-environment
            environ
            name
            (seval (define-value-exp def-exp) environ))))))

;; Function definition
#;
(define (func-define-exp? exp)
  (and (list? exp)
       (= (length exp) 3)
       (list? (cadr exp))
       (>= (length (cadr exp)) 1)
       (andmap symbol? (cadr exp))
       (eq? (car exp) 'define)))

;; "begin" expression
(define (begin-exp? exp)
  (and (list? exp)
       (>= (length exp) 1)
       (eq? (car exp) 'begin)))

(define (begin-statements exp)
  (cdr exp))

(define (seval-begin-exp exp environ)
  (seval-statements-block
   (begin-statements exp)
   environ))

(define (seval-statements-block stmts environ)
  (let [(n_stmts (length stmts))]
    (cond [(= n_stmts 0) (void)]
          [(= n_stmts 1) (seval (car stmts) environ)]
          [else
           (seval (car stmts) environ)
           (seval-statements-block (cdr stmts) environ)])))

;; lambda expression

(define (lambda? exp)
  (and (list? exp)
       (>= (length exp) 3)
       (list? (cadr exp))
       (andmap symbol? (cadr exp))
       (eq? (car exp) 'lambda)))

(define (lambda-header exp)
  (cadr exp))

(define (lambda-body exp)
  (cddr exp))

(define (seval-lambda exp environ)
  (make-lambda (lambda-header exp) (lambda-body exp) environ))

(define (make-lambda argnames body environ)
  (lambda args
    (if (not (= (length args) (length argnames)))
        (error "Arity error, expected/received:" (length argnames) (length args))
        (let [(localenv (make-environment environ))
              (argmap (map cons argnames args))]
          (for-each (λ (pair) (define-in-environment
                                localenv
                                (car pair)
                                (cdr pair)))
                    argmap)
          (seval-statements-block body localenv)))))
          

;; set!

(define (set-exp? exp)
  (and (list? exp)
       (= (length exp) 3)
       (symbol? (cadr exp))
       (eq? (car exp) 'set!)))

(define (set-exp-name exp)
  (cadr exp))

(define (set-exp-value exp)
  (caddr exp))

(define (seval-set-exp exp environ)
  (set-in-environment
   environ
   (set-exp-name exp)
   (seval (set-exp-value exp) environ)))

;; Tests

(define code
  '(begin

     ;; Closure
     (define foo
       (lambda (x)
         (lambda (y) (+ x y))))
     
     (display ((foo 5) 19))
     (newline)
     (define bar (foo 10))
     (display (bar 3))
     (newline)

     ;; Set
     (define z 10)
     (display z)
     ((lambda () (set! z 11)))
     (newline)
     (display z)
     ))


(seval code globalenv)