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

(define (seval ...)
    ...

)

(define (sapply ...)
    ...
)


