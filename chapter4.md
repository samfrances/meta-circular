# Chapter 4 : Metalinguistic Abstraction

In some sense, this chapter is the final destination of the first
three chapters of the book.  Up to now, you've learned about the
nature of computation and various programming abstractions around data
and evaluation.  However, in this chapter you essentially create your
own programming language interpreter.  Not only that, your interpreter
will be able to run all of the programs presented up to now.

Once you have your interpreter, you can then start modifying it to behave
in different ways.

## Eval

In languages like Scheme and Python, there is often an "eval" function to evaluate
code:

```
>>> eval('3 + 4 * 5 + 10')
33
>>> exec('for i in range(5): print(i)')
0
1
2
3
4
>>>
```

We're going to make something very similar to this.  However, the one big twist
is that in Scheme, the programs themselves are data structures that can
be easily manipulated.

Remember quotation?

Try defining this:

```
(define prog 
   '(define (fact n) (if (= n 1) 1 (* n (fact (- n 1))))))
```

Now, try pulling it apart:

```
> prog
'(define (fact n) (if (= n 1) 1 (* n (fact (- n 1)))))
> (car prog)
'define
> (cadr prog)
'(fact n)
> (caddr prog)
'(if (= n 1) 1 (* n (fact (- n 1))))
>
```

The fact that a Scheme program is represented as Scheme data opens up a variety of
new possibilities.  It also makes it easy to manipulate such programs using all of the
tools that you already know.   This is in contrast to most other programming languages
where you'd need to write a lexer, a parser, abstract syntax trees, and more advanced
constructs to manipulate code.

## Evaluation as a Process

Another big idea concerning "eval" is that all computation is a process of evaluation and
application.   For example, consider this:

```
(+ (* 3 4) (* 6 7))
```

To evaluate the outer `+` operator, you first evaluate the subexpressions:

```
(+ 12 42)
```

You then apply the `+` operator to get 54.

It turns out that all programming languages are designed as a kind of dance
involving "eval" and "apply."

* When are expressions evaluated?
* How are expressions evaluated?
* When are procedures applied?

It turns out there are many possible design choices in how this works.
The decisions that you make change the nature of the programming language that you
create.

## The Metacircular Evaluator

We're going to build the "metacircular evaluator" as described in [Section 4.1](http://sarabander.github.io/sicp/html/4_002e1.xhtml#g_t4_002e1).
In a nutshell, it's an evaluator that's written in the same language as is being evaluated
(i.e., A Scheme program that evaluates Scheme programs).

I'm going to do this part of the course as a group coding exercise.   Reading this section of the book
is quite challenging, there are many moving parts, and as written, it is very hard to make
incremental progress.   As such, I will try to simplify and guide you in the process.  I will also
use some features of Racket to help reduce the amount of code involved.

As a stretch goal, we will also try to implement either "Lazy Scheme" as described in section 4.2
or "Amb" as described in section 4.3.

Please find the file `meta.rkt` to start doing your work.








































