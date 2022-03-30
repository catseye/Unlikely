Tests for Unlikely
==================

    -> Tests for functionality "Parse Unlikely Program"

Here is a syntactically correct program.

    | class Count(Count,Chain,Print,Add) extends Continuation
    | 
    | class CountForever(Count,Chain,Print,Add) extends Program {
    |   Count c;
    |   method continue(Passive accumulator) {
    |     c = new Count(Passive,Count,Chain,Print,Add);
    |     goto c.continue(new 1(Passive));
    |   }
    | }
    | 
    | class Count() extends Continuation {
    |   Count c;
    |   Print p;
    |   Add a;
    |   method continue(Passive accumulator) {
    |     c = new Count(Passive,Count,Chain,Print,Add);
    |     a = new Add(Passive,Chain);
    |     a.value = new 1(Passive);
    |     a.next = c;
    |     p = new Print(Passive,Chain);
    |     p.next = a;
    |     goto p.continue(accumulator);
    |   }
    | }
    | 
    = 

And here is one which is not syntactically correct.

    | class Hello(Print,Chain,Stop) extends Program {
    |   Print p;
    |   method continue(accumulator) {
    |     p = new Print(Passive,Chain);
    |     p.next = new Stop(Passive);
    |     goto p.continue(new "Hello, world!"(Passive));
    |   }
    | }
    ? ArtefactNotFoundError
