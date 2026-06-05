# What is property-based testing?

You can think of a test as consisting of two parts:

1. A scenario
2. A set of checks

The scenario is "I did a thing", and the checks are "here is what should have happened when I did that thing".

Each of these can vary in how specific they are.

1. Here is the exact thing I did, and here is the exact thing that should have happened.
2. Here is the exact thing I did, and here are some things that should be true about the result.
3. I did something like this, and this is the exact thing that should have happened.
4. I did something like this, and here are some things that should be true about the result.

Concretely:

1. Here is a series of interactions with my web-application, and here's what the screenshot of the final result should look like.
2. Here is a series of interactions with my web-application, and every fetch should have returned a 200 or a redirect.
3. I inserted three unique keys into my dictionary, and the result should be that the dictionary should have this exact structure.
4. I inserted three unique keys into my dictionary, and the dictionary should now have size 3.

These four categories roughly correspond to:

1. Snapshot testing (AKA golden master testing AKA expect testing)
2. Example-based testing (what you probably think of as "normal software testing")
3. Differential testing (comparing two implementations of the same API and asserting that they get the same result)
4. Property-based testing (what this book is about)

None of these are truly distinct categories, and all of them are great in some contexts. This is important to remember: When learning about property-based testing, it's easy to get excited and think all of your tests should be property-based tests. Resist that urge. Property-based tests are part of a complete ~breakfast~ test suite, not the whole of it.
