All right, here I am again and today we're going to move uh slightly
0:1010 secondsforward. We're going to talk about MCP which is our model context protocol and uh why it was acquired, why it was invented and what led to this particular
0:1717 secondsjourney. uh a lot has changed since the introduction of MCP as well and we're going to cover the new framework u that
0:2525 secondsI believe is going to be the future as well and that will allow you to uh create apps on the fly. Uh what you also need to uh sort of have a belief with me
0:3434 secondsis that software as we know is not going to be continuing u as we know for example we download software and when
0:4242 secondsthen we use them uh we're not going to see that continuing forward for quite some time because um the whole landscape is changing and we don't need software
0:5050 secondsfor the whole uh thousands of features they provide. We only need them for some of the features that we need at that particular moment. So you're going to see these micro apps that just gets
0:5858 secondscreated on the fly and uh they are essentially not there when we don't need them. So that's the direction the whole world is going to be going and uh if you
1:071 minute, 7 secondsare following uh Twitter or LinkedIn you're going to see that every day there's someone who's just creating new apps. So creating application is not going to be mo but creating them on the
1:161 minute, 16 secondsfly within let's say a second of request is going to be what uh is going to be super exciting and that's where the session is going to be going by the time
1:231 minute, 23 secondswe end today. Now I hope you're doing your assignments um that uh I've been pushing uh so assignment 1 2 3 should be
1:311 minute, 31 secondsdone by now. If not then then uh you can submit them as soon as possible. But um today's assignment is something that
1:391 minute, 39 secondsI've been pushing for the Chrome plugins because uh it sits on your browser. You spend most of your time on your browser so you can actually make something uh that you're interacting with some
1:471 minute, 47 secondswebsites or some your of your own personal things like Gmail or maybe G Drive. But you're free to make any application. Uh me just saying that
1:561 minute, 56 secondsGoogle Chrome applications needs to be submitted doesn't mean you have to make one. Uh you can make anything that of your choice. But today uh by the time we end what you're going to see is uh you
2:042 minutes, 4 secondscan actually uh make UI on the fly. And that's the uh game changer that I believe MCP has enabled and where the
2:132 minutes, 13 secondsagents also going to be going. Now uh first again a little bit of Python as I believe that even though uh these
2:202 minutes, 20 secondslanguages are soon going to be um sort of dinosaurs for us but uh we still need to know them. We still need to know who
2:262 minutes, 26 secondswas the T-Rex and who were the other uh dinosaurs that existed earlier. So uh in
2:342 minutes, 34 secondsthe last session we discussed a singio uh singio was required because it's possible that we want to access lot of features at the same time lot of tools
2:412 minutes, 41 secondsat the same time we are making a lot of requests at the same time a very simple example would be uh let's say uh you
2:482 minutes, 48 secondswant to search internet for stock um market behavior or company behavior or you want to understand more about Tata
2:552 minutes, 55 secondssteel or some incident that happened in that case you may not want to visit one website understand then second website it's going to be very slow Right? Even
3:033 minutes, 3 secondsthough internet speed might be fast but doing things sequentially is not going to be super helpful. U having said that
3:103 minutes, 10 secondseven if let's say internet speed was fast and we go through all the websites download all the data at once the websites that we get back they have lot
3:183 minutes, 18 secondsof HTML CSS and JavaScript all around it. So we need tools that scrape them that extract the text and then collect that right. So that also takes time. So
3:273 minutes, 27 secondsa lot of things that is going to take one time one after the other. So we don't want that. We want everything to happen in parallel and whenever we do things in parallel we need something
3:353 minutes, 35 secondslike async.io. Now async IO is uh something we touched upon last time as well. We define functions using a sync and wherever you add a sync in front you
3:443 minutes, 44 secondscan gather them and run run at run them uh in parallel. Now the time of getting the result is same as the time it takes
3:513 minutes, 51 secondsfor the longest one. There are other features also that we can ask clot to go through where whatever is getting finished we can use that. We are going
3:583 minutes, 58 secondsto be using that feature especially when we talk about our final architecture for the agent where we'll have uh the graph network where as soon as a node is done
4:064 minutes, 6 secondswe'll get the results back but till then we need to live with a sync IO then we cover code or interact is something that uh you need to know how
4:144 minutes, 14 secondsto debug how do we go inside the code and understand what's happening at that particular moment we discussed that code or interact is simpler one but after
4:214 minutes, 21 secondsthat we have PDB uh now just need to write uh PDB And then you can actually get uh really
4:304 minutes, 30 secondsinside the code and understand what's happening there. You can add checkpoint also. So it's way more simpler model as well. So inside the code we understand
4:384 minutes, 38 secondswhat has happened till that particular point. Change the key, change the uh prompt or maybe uh change the URL. So
4:464 minutes, 46 secondsany setting you want to change while the code is running is something that is possible using these things. Now then we have env. Nowv I've been using it. You
4:554 minutes, 55 secondsprobably might be using it also. uh but we need to just highlight it a bit on what it is. Now env is a Python module that helps us manage our secret. Uh it's
5:035 minutes, 3 secondsav file where we put our secrets like uh Gemini API or any password you have or any key that we have and in the get
5:115 minutes, 11 secondsignore we say that please don't upload file as well as something that you keep secure. Uh ENV file is now send into environment. You can keep it outside
5:195 minutes, 19 secondsyour environment also and then it is pushed in. Now once that happens then from env import load env we can load
5:275 minutes, 27 secondsthat key and then all the keys are available for our programs function there some of the basic things that we need to be aware of and you need to remember otherwise you may push your
5:365 minutes, 36 secondscode with the secret keys that should not be done now then we have Python decorators this is the I'll say the DNA
5:445 minutes, 44 secondsof the whole NCP right so decorator sounds like we are decorating something it's literally a wrapper and whatever
5:515 minutes, 51 secondshappens runs inside the wrapper is our function but whatever happener outside is a decorator. So decorator provides some additional features to the
5:585 minutes, 58 secondsfunctions that are written. Now that is what makes any function into a MCP uh related call also. But the function is
6:066 minutes, 6 secondsvery simple. Decorator takes a function and returns a modified function. So we can take a function uh let's say scan
6:156 minutes, 15 secondsthis website and return a modified function. What can be modified? We can't modify the actual core functionality but we can modify whether the URL going in
6:246 minutes, 24 secondshas https whether the o was required and then we are forcing our a function to access it how much time it took uh what
6:326 minutes, 32 secondswas the speed of the functioning or the what the speed taken uh to process that kind of function. So all those things can be added. So we can add lot of additional features on top of function.
6:406 minutes, 40 secondsRight? So that is what decorators are very simple. We just need to write at my decorator on top of any function and that becomes a decorator. Now as I said
6:486 minutes, 48 secondswe all have been doing wipe coding but you need to know these things exist and when you see at kind of symbol you don't worry that suddenly you're looking at
6:566 minutes, 56 secondsalien language we don't want that then we discuss try. Uh trying is good uh if you don't try we don't know
7:047 minutes, 4 secondswhether we'll fail or succeed. So trying is very important in life but we need to have exceptions also. Uh trying something and then failing and knowing
7:117 minutes, 11 secondswhy we failed is very important. And unlike other languages where things crash, Python is sort of designed to work with the crash or work with the exception, it's a very different feel.
7:217 minutes, 21 secondsUm, if you come from C or C++ where things crash, it just says I give up, right? But in Python, we are supposed to design functions that catch exceptions
7:307 minutes, 30 secondsand allow us to continue. That is what we do in here uh in Python. So you're seeing here, we're dividing by zero. Uh when we have divide by 0, we can just
7:387 minutes, 38 secondscatch all exceptions. bit here better is that we catch uh zero division error that will tell a function that okay something was zero we were trying to
7:477 minutes, 47 secondsdivide by zero and we can take uh the next decision based on that right so so uh exceptions are not bad in Python exceptions are actually there to make
7:567 minutes, 56 secondsour functions more I'll say deterministic like what happens when something happens or something breaks now try catch for example JSON or maybe
8:058 minutes, 5 secondsO key is not there or maybe you've hit your rate limit which I keep seeing now you you as you're discussing right now all of those things are um sort of we
8:138 minutes, 13 secondscan contain here and make sure the function doesn't crash or the program doesn't crash. So if your program is crashing, you've not written try and catch. So you can just ask your claude
8:218 minutes, 21 secondssmartly first raise of colors and then ask your claud hey have you written uh try catch and cloud can just oh I'm sorry I I forgot right? So you can
8:298 minutes, 29 secondsactually be better in claude in some direction.
8:338 minutes, 33 secondsNow here's a sort of a complex code which is using a sync and we are gathering task in a list and then we are
8:408 minutes, 40 secondsputting the task in the uh gather function. Slightly more complicated way of looking at it. So now you can see this list can have hundreds of functions
8:488 minutes, 48 secondsright or hund h h h h h h h h h h h h h h h h h h h h h h h h h h h h h h h h h h h h h h h hundreds of web URLs. That's how publicity works. That's how your Google uh gemini would work or openi
8:558 minutes, 55 secondswould work. So under the hood uh coding ideas on what those guys are doing okay now let's come to today's sessions
9:039 minutes, 3 secondsright now today's session is on MCP. MCP is called model context protocol. Now u before we directly jump into MCP we need
9:129 minutes, 12 secondsto understand why we are here like what has forced people to write MCP and uh what are the benefits and I'll say uh
9:219 minutes, 21 secondsdrawbacks also because there was a big drawback when it came it has improved a lot since then uh now you don't have to worry uh it was very very worrisome when
9:299 minutes, 29 secondsit came first time and I had to teach people because it's totally confusing it's still going to be bit confusing today because you're looking for at it for the first time but uh believe me it will get very very simple as we uh move.
9:419 minutes, 41 secondsOkay. Now the first thing that we need to remember is that we started with the foundation LMS. Now we are going back to 23 24 when chart GPT was first launched
9:509 minutes, 50 secondsand we were chatting with it and it was answering like a human and everyone was surprised oh how good this is. We could ask it talk like a 5-year-old talk like
9:589 minutes, 58 secondsa talk like Albert Einstein or um um anyone can Morgan Freeman as will just
10:0610 minutes, 6 secondsdo that right. So when we introduced LM for the first time u the coherence or u
10:1410 minutes, 14 secondsthe way they were speaking was very good the responses were really good but the problem is uh they were designed to
10:2110 minutes, 21 secondsanswer questions who's the president of United States of America uh it's going to tell uh that okay based on my knowledge it is let's say Barack Obama
10:3010 minutes, 30 secondsbecause it was trained that that particular time now that also happened after we have done the SFD part right now we discussed this in the first two
10:3810 minutes, 38 secondssessions that pure LM is just completion. Now if you just ask who's the president of United States on LM it's just going to say the most
10:4510 minutes, 45 secondsinfluential person in the world before SFT moment we do SFT it's going to remember that okay I was trained till uh
10:5210 minutes, 52 secondslet's say 20 24th December and at that time this was the president and he's going to give you that particular answer it depends on till what time it is
10:5910 minutes, 59 secondstrained so uh we discussed the SF part so this is where we discuss again discussing SFT uh if you have not done SFT and you say write an email stating
11:0811 minutes, 8 secondsthat I'll be on leave today it's just going to say and send also Right? It's literally finishing the sentence based on whatever is available
11:1511 minutes, 15 secondson the internet. Now that's where SFT came in. SFT suddenly turned things around. And in case of uh uh when we did
11:2411 minutes, 24 secondsSFT, it could actually answer. It could actually work like a chatbot. You could talk to it. You can get responses. It will draft emails. Uh it could draft
11:3311 minutes, 33 secondslegal agreements. But still in a text mode, but it improved a lot, right?
11:3711 minutes, 37 secondsRight. So, SFT literally allowed it to follow instructions and we have instruction following data sets also.
11:4311 minutes, 43 secondsThere are a lot of data sets available but this is actually the core. Uh in fact I shared in last session also that people keep copying opus. Uh in fact
11:5211 minutes, 52 secondsyou're going to moment you go to hugging face just write opus distill and you'll see every single function or every single model that release like gamma 4
12:0012 minutessomeone would have taken gamma 4 taken the data from opus and then distill on it. This still essentially means uh you have a bigger good model uh you try and
12:0912 minutes, 9 secondsreplicate the answers as that model would have given on a smaller model.
12:1312 minutes, 13 secondsIt's a very easy process to do and model sort of starts acting like uh opus. So that's SFT essentially. We can have a
12:2112 minutes, 21 secondsbigger model that teaches small model or we can have good data set that is teaching the small model or a big model in respect to how do we answer a
12:2812 minutes, 28 secondsparticular question. Now, that still answers a question. That still doesn't answer the question that we like to hear or we like to see. Sometimes when you're
12:3612 minutes, 36 secondsasking a question, you want a brief response. Sometimes you want a long response. Sometimes you want a diplomatically correct response.
12:4212 minutes, 42 secondsSometimes you want just the response like Grog. Now, in that case, we have this RLF that comes in which is reinforcement learning with human
12:5012 minutes, 50 secondsfeedback where human provides additional feedback. I don't like your answer. Uh it might be correct. I just don't like how you structured it. Uh for example, I
12:5812 minutes, 58 secondsdon't like you calling me a fool. it's okay if you're finding my mistakes those sort of things. So uh we strip that part out and make behave uh much more
13:0613 minutes, 6 secondsobedient. So R HF is not for adding intelligence to the model or adding uh features to the model. R LF literally
13:1513 minutes, 15 secondsfor making model behave in a certain way society believes that it's not going to be bad right that's where LHF comes in.
13:2213 minutes, 22 secondsSo but moment we do SFT and RHF leave notification. uh for example if you ask write an email stating that I'll be on leave today it will actually draft the
13:3013 minutes, 30 secondsproper email right so that's the SFT part that we discussed and what is the square root of something and uh if you ask what is the current GDP of India it
13:3913 minutes, 39 secondswill fail right now here is the next problem because the questions that we ask are not only going to be just write
13:4613 minutes, 46 secondsan email or just theoretical nature for example what are the in fact that answer also keeps
13:5413 minutes, 54 secondson changing every four five years like tell me about the states in the uh in the country now every four five years we have a new state or new urine territory
14:0214 minutes, 2 secondsright that keeps popping up in the countries and the answer is going to be old so there are questions that need real-time data the moment we need
14:0914 minutes, 9 secondsreal-time data you can think about we need the access to the internet so certainly the model needs to know that I've been asked something for which I have to go to internet and fetch the
14:1814 minutes, 18 secondsdata right so certainly those things are are getting out of hand and we may ask some stupid questions also for example what is the square root of 14.5 to 321
14:2714 minutes, 27 secondsbecause we're too lazy to open a calculator and I don't know how many how many of you have opened calculator uh in recent times most of the people use Google search for calculation also u so
14:3714 minutes, 37 secondsthose become problem and openai and others started seeing that okay users have started asking these questions what do we do about them that's where we have
14:4514 minutes, 45 secondsa function calling right so what is function calling you you use in last session in function calling a model determines that the answer to this query
14:5314 minutes, 53 secondscannot be given just based on memory. I need to have another another tool that I can need to call which will give me the
15:0115 minutes, 1 secondanswer. Now in that case for example if you ask what is the square root of 14.5 uh 232 lm is going to decide I can't do it. I need to call an external function.
15:1215 minutes, 12 secondsThe external function will be given 14.5232.
15:1515 minutes, 15 secondsIt's going to calculate a square root and respond back and that's when you're going to get the answer. All of that happens in the background. Right? All of that is happening. Uh when we are being
15:2415 minutes, 24 secondsshown that circle or something that's waiting that's function calling. So fun moment function calling came everything changed right because suddenly now uh
15:3215 minutes, 32 secondsthe uh limit is like infinite right you can connect to email you can connect to Gmail you can connect to Uber you can
15:4015 minutes, 40 secondsconnect to Swiggy anything that you can think of becomes possible. So you can get the weather data, you can get the uh flight status, you can uh link it to the
15:4915 minutes, 49 secondsnews, you can link it to the uh recent data and combine them and then give the proper answer. Right? For example, if
15:5615 minutes, 56 secondsyou ask hey uh has a how do I apply for birth certificate in the country? It it can give you some
16:0316 minutes, 3 secondsanswer. There's no I need particularly in Karnataka for instance. So now it knows need to go online look for uh internet search based on Karnataka or
16:1116 minutes, 11 secondsBangalore. it's going to come back, read the website and give you the data. So all of that is function calling, right?
16:1616 minutes, 16 secondsSo function calling is what makes an error even better. Uh it's still not sort of an agent yet because um we have
16:2416 minutes, 24 secondsa slightly different uh feel about agent but technically we've just made an agent. So moment an LM can call a function, it becomes an agent. That's a
16:3216 minutes, 32 secondstheoretical definition of what an agent is. Now there are other philosophical definition also. It needs to be autonomous. It needs to have its own autonomy. needs to be uh not triggered
16:4116 minutes, 41 secondsby human all of that is like people pushing the boundaries of what agents can do but literally this is agent and that's what we did in last session also
16:4916 minutes, 49 secondsso now if you can ask what is square root of this number or what is the GDP current GDP right this number is important what is the current GDP of India so you can go online fetch data
16:5716 minutes, 57 secondsand then respond back now this allowed LM to provide accurate right because now it has a grounding grounding means it
17:0517 minutes, 5 secondshas a source using which it is reading up to date uh again because it is fetching the latest data and computationally precise responses. It's
17:1317 minutes, 13 secondsjust not like telling you an approximate number, it's actually giving the correct number. So all of these things become possible. So moment we had that user uh quickly started demanding more, right?
17:2417 minutes, 24 secondsAnd this is something that you would have wanted at some time when you're talking to your charg as well like uh can you send this email actually can you
17:3117 minutes, 31 secondsopen my excel and change it right? You just don't want that alert tells you do something and you need to do something. Uh and it all started from coding also.
17:3917 minutes, 39 secondsYou're asking charge GPD I want to write a code what do I do? RGB is going to give you a code you copy paste and it crashes then you're going to get frustrated you're going to go oh it
17:4717 minutes, 47 secondscrashed and I'm not sure how many of you have gone through that particular phase but 2024 was that that's what led to cursor right message this on telegram
17:5417 minutes, 54 secondsnot possible book a flight for me not possible so there limited set of tools that charge GP claude or gemini can provide on the internet because it has
18:0318 minutes, 3 secondsuh no access to the other tools that are like private to me or that I use that's where the definition of agents sort of
18:1018 minutes, 10 secondsstart becoming more fruitful for us. So that pushed the AI in a direction where we allow LLM to take more actions,
18:1818 minutes, 18 secondsright? Take action in the real world which is linked to my personal data um APIs that are very very private to me
18:2618 minutes, 26 secondsand uh APIs that are private to our company and start getting details from there. Now that is where we had the rise of agent AI. Now we don't think of
18:3518 minutes, 35 secondscursor as an agent but cursor is one of the first agent that actually came out which people uh realize that how useful it can be. Cursor led to a lot of
18:4218 minutes, 42 secondsdifferent things and a lot of people fking it into lovable into perplexity.
18:4718 minutes, 47 secondsAll of those are sort of I'll say um different variants of what cursor was trying to do. Cursor is as you know
18:5518 minutes, 55 secondsalready probably you're using Gemini because it gives you free credits but cursor is what let people write the code edit a code look at the bug and fix it
19:0319 minutes, 3 secondsagain and so it works in that particular loop. Now if you have done the last assignment uh not the last this one if you've done the assignment four which
19:1119 minutes, 11 secondsyou haven't uh there's a CRUD feature we're going to look at it crud is basically uh creation editing update and deletion right so if you want to edit a
19:2019 minutes, 20 secondsfile we need to be able to open it we need to be able to edit it we'll need to be able to update it and we possibly need to delete some old files also so
19:2819 minutes, 28 secondsmoment we provide these four features to an LLM it can do wonders and that's what cursor did and update, open a new email,
19:3719 minutes, 37 secondsupdate a new email or update the contents of the email, send that email, delete that email. Right? Same goes for calendar, same goes for flight, same goes for your banking account also.
19:4819 minutes, 48 secondsRight? So there are some limitations we will not like to cross. But that's where we are going. So the need of actionoriented AI led to the agentic AI
19:5619 minutes, 56 secondswhere uh we just don't want it to just connect to internet fetch data. That's still static, right? Me going online getting some data, it's still static in
20:0420 minutes, 4 secondsnature. That's where even J RGBT or Gemini online are there. If you think about it, they can't go and edit things for you. They can read a static stuff
20:1220 minutes, 12 secondsand come back to you, right? We wanted something that can edit things also, delete things also, manage for us, uh do a chron, which is scheduling something
20:2020 minutes, 20 secondsfor us, which would mean that every 4 hours check something for us, uh uh log to something for us. So all of those
20:2820 minutes, 28 secondsrequire multihop sessions or multihop steps. Again, we are going to be covering them now.
20:3520 minutes, 35 secondsUh here's a good example. Accessing calendar to schedule meetings. Uh sending message via telegram. Performing online transactions. These are not
20:4220 minutes, 42 secondssingle steps. These are multi-steps. Now and you can think about what all humans would want. Okay, this is possible. Then
20:5020 minutes, 50 secondscan you come on my computer uh look at my screen work with Autodesk make look at the PDF file of a part I want
20:5920 minutes, 59 secondsactually make that 3D PD uh 3D part also right? Our dreams are infinite. what I just spoke has been solved is being
21:0621 minutes, 6 secondssolved in the last one week. If you go on Twitter, you're going to see someone is releasing. Hey, I just asked uh GPD 5.5 to make a a 3D printer for me.
21:1521 minutes, 15 secondsLiterally, if you go on Twitter right now, people just posting that I asked GPD 5.5 or cloud opus 4.7 to make a 3D
21:2321 minutes, 23 secondsmodel for me. That is where we have reached out. So, what has been changing?
21:2721 minutes, 27 secondsInitially, this was implementing one application at a time. Um Slack is integrated on so you might
21:3521 minutes, 35 secondsremember OpenAI apps right Slack is integrated Uber is integrated then we have let's say uh bookings.com is integrated Google calendar is integrated
21:4421 minutes, 44 secondsso we kept on integrating these applications to provide a feature the problem is humans have infinite dreams infinite desires we have infinite
21:5221 minutes, 52 secondsapplications you can't just keep on integrating all of them and integration is difficult right imagine that um you
21:5921 minutes, 59 secondsare Bengali and uh you get a Punjabi uh daughter-in-law it's going to be nightmare or if you are
22:0822 minutes, 8 secondsTamilian and you get someone from North India who joins your family man you will just not agree on how sambar should be right it's going to be
22:1722 minutes, 17 secondsdifficult one of you is going to be speaking Java other's going to be speaking Python then you'll have a C then you'll have C++ then you have forran and everyone wants to write code
22:2622 minutes, 26 secondsin a different way someone wants to follow particular I don't remember uh I don't know you will remember or not but uh six seven years ago when AI was not
22:3422 minutes, 34 secondsthere uh in the coding front we had these concepts that this is how code should be written right and we have a
22:4122 minutes, 41 secondsview and model and other stuff all of all of the ways in which people believe like a religion that this is how software needs to be written and how
22:5022 minutes, 50 secondssoftware are written like that now if you look at how Google writes software how Apple writes software very very different so how do we start integrating
22:5922 minutes, 59 secondsit. This this started reaching our limitations like how do we um make people essentially write software in such a way that LMS can interact. Now
23:0823 minutes, 8 secondsI'm suddenly reading Google. Okay. And that is also sort of impossibility because Google will have billions of
23:1623 minutes, 16 secondsapplications, right? I I'm not sure do you even know how many applications Google provide. There's Gmail. These are ones I can recollect. You can also
23:2423 minutes, 24 secondsrecollect these. Drive. Drive itself has word. Then you have uh uh their slides and then their excel sheet. And then you
23:3223 minutes, 32 secondshave uh forms. Then inside you have Gmail of course. Then you have Google calendar. Then you have Google meet. Do you have uh things that keep on expiring
23:4023 minutes, 40 secondsthe Google one was there comes in and goes away. So like thousands and thousands of application and then suddenly your company your manager or
23:4723 minutes, 47 secondsyour uh management will decide no you're not going to use Google you're going to use Microsoft. So suddenly you have Microsoft Outlook Microsoft 365
23:5623 minutes, 56 secondsMicrosoft 748 and so on and so on and suddenly some nationalists will be there in your company which is going to say no we're going to use Zoho. So now you'll
24:0424 minutes, 4 secondshave Zoho books and Zoho accounts and other stuff and someone uh like the chairman will come and say no I've been using Yahoo since I was born 74 years
24:1224 minutes, 12 secondsago. Uh we going to be using Yahoo. So the email is on Yahoo and you have to integrate Yahoo also. So you can imagine the nightmare that is now being thrown
24:2024 minutes, 20 secondsat people. You have to integrate all this into LLM. Now LM is sitting quietly and just looking at humans
24:2824 minutes, 28 secondsbecause it can't do anything else. We're just pushing and pushing and pushing different application that LLM somehow has to understand and react accordingly
24:3624 minutes, 36 secondsalong. It has to write code for that. It has to structure the uh message for that. Sometimes the subject is first the uh messages later on and the O key is
24:4524 minutes, 45 secondsthe end. Sometimes O key is there first then subject is next and then text is there. Sometimes you can send a PNG but sometimes you have to send a bit map.
24:5224 minutes, 52 secondsSometimes you have to send uh the encryption encrypted data. Sometimes you can't send a 32 uh bit PNG. you have to send um you can you probably can
25:0125 minutes, 1 secondunderstand like if it is government of India then PDF has to be 32 KB upload your photograph high resolution photograph clear crystal clear nose
25:0825 minutes, 8 secondsshould be visible in 32 KB or upload the I don't know if you applied for Aadhaar address change or not upload your full
25:1625 minutes, 16 secondslease agreement you bought a new house you need to change your Aadhaar card upload your full lease agreement sale deed agreement which is like 500 pages
25:2425 minutes, 24 secondslong because you wanted it to be that way in 1 MB And how do how do you do that right? So all these things are
25:3225 minutes, 32 secondsthere. So LM also faces some issue. So first of all diverse uh religious tracks
25:3925 minutes, 39 secondsright we have large number of diverse uh states and religion in software we have to integrate all of that somehow like
25:4625 minutes, 46 secondsone L&M company has to integrate all of them. Then second is inconsistent API structure or you can read inconsistent Indian government websites right it's
25:5525 minutes, 55 secondsexactly the same thing. uh Indian railway works in a different way compared to IT department compared to GST compared to input export uh compared to the fire department compared to ESG
26:0426 minutes, 4 secondscompared to BBMP. uh if you want to um for example pay your property tax if you are within the 5 kmters of this area
26:1226 minutes, 12 secondsthis a different website outside the 5 km area that website sometimes website is down then there's authentication complexity I
26:2026 minutes, 20 secondsdon't know you have you will start having as accounts very soon as first tell me your email id so you tell the email id oh your email ID is correct
26:2726 minutes, 27 secondsgive me the password now so we give the password no give me the capture also give the capture no okay now open your phone give me the two off also
26:3526 minutes, 35 secondsIt's like like you have to keep on authenticating in different ways. Now sometimes Google is going to let you login. It's going to say on the phone itself going to say open your Gmail and
26:4326 minutes, 43 secondsgo there and select a number. You go to Gmail, you select that number, come back and you say okay your session expired try again. So you are stuck in that particular loop. Sometimes from mobile
26:5226 minutes, 52 secondsphone this happens a lot of times uh if you are trying to access free internet connection on on airports. Uh you connect to Wi-Fi it opens the screen it
27:0027 minutessays send OTP. Now to get the OTP you have to go out on the SMS app get the OTP and you come back gone again right and you have to get the screen back
27:0827 minutes, 8 secondsagain. So this authentification complexity is a lot right we don't trust people and especially if they are from uh different states so or different
27:1627 minutes, 16 secondslanguages sorry or different uh IP addresses so there's a bit of problem there and that brings us to this particular problem which is the
27:2327 minutes, 23 secondsscalability issue how do we scale AI was supposed to solve poverty it will not but like that was the dream so how do we
27:3127 minutes, 31 secondsscale this how do we make sure that it can connect to every single possible application that's where anthropic comes That's where anthropy comes in and says
27:4027 minutes, 40 secondsthat okay what if we write a protocol what is a protocol by the way protocol is set of
27:4727 minutes, 47 secondsguidelines u that sits on top of any other function and makes that function behave exactly as I want that sounds
27:5627 minutes, 56 secondslike a decorator what does a decorator do
28:0428 minutes, 4 secondsdoesn't matter what function goes in the structure output structure can be fixed right so if you can take your old uh API
28:1228 minutes, 12 secondsit can be written in 1974 but if it goes through this particular wrapper it will behave exactly as we
28:2028 minutes, 20 secondswanted it right it will behave exactly as the spec written in that MCP protocol that's what anthropic did entropic was the first one uh which came out with the
28:2828 minutes, 28 secondsMCB protocol and the logic was very very simple right so logic is that uh to solve this integration challenge the
28:3628 minutes, 36 secondsauthentification any other stuff. MCP is going to force people to follow exactly the same kind of output. Now what does the LM need to know as same input by the
28:4428 minutes, 44 secondsway same input and same output. So input goes inside the MCP a decorator gets structured based on how we want uh we
28:5128 minutes, 51 secondswant Ganesh Ganesha Lord to be prayed first then Vishnu and then Laxmi and or maybe Laxmi and Vishnu based on or maybe Shiva like all of that is happening in
29:0029 minutesbetween or you have a particular schema where you wash your hands first then eat or maybe you eat first and then wash your hand all of that whatever
29:0829 minutes, 8 secondsapplication software wants us to do goes inside the MCP function but MCP function is wrapped around this thing which forces it to take exact Exactly the same
29:1629 minutes, 16 secondssame data and gives exactly the same output right when I say exactly I'm saying the protocol basically input
29:2329 minutes, 23 secondsfunction name uh type goes in uh output is defined type goes out so that thing is sort of structured the moment you fix
29:3029 minutes, 30 secondsthat you can automate everything and that is what is happening since last I'll say uh one year it's not very old
29:3829 minutes, 38 secondsso now we can work seamlessly with any application or any old application underlying technology doesn't matter it
29:4529 minutes, 45 secondsmight do C++, Python, Rust or Go. U and it's little like USB, right? Whatever you put on USB, connect to your computer
29:5329 minutes, 53 secondsand we can just transfer it. That's what really MCP is. And writing MCP function is also very simple. Uh it's literally you write a function on the top you just
30:0130 minutes, 1 secondwrite at tool. That's all right. Can you imagine? Write any function you want. On top you just say add tool and becomes
30:1030 minutes, 10 secondsMCP tool, right? We're going to see that today. But that's the power of MCP. So now the benefit is a single protocol and
30:1730 minutes, 17 secondsagain what is a protocol? Protocol is how we going to communicate right? How do we communicate in India? We say namaste and then we ask how are you? You
30:2630 minutes, 26 secondswill ask me I'm good. How are you? I'm also going to I'm also good and just we'll just walk away right we'll never going to see each other again. That's
30:3430 minutes, 34 secondshow we greet people in India. Uh in in Japan for example when you meet someone you just like go ahead the other guy both and then walk away. we don't don't
30:4330 minutes, 43 secondstalk to each other. So that that sort of protocol like how are we going to introduce each other and after that if you have to shake hands, if you have to
30:5030 minutes, 50 secondsexchange notes, what happens inside? So that is fixed. So function can do anything it wants internally. So that means that now the model needs to learn
30:5930 minutes, 59 secondsone thing which is the protocol. How does MCB protocol work? If it knows it can work on any function in the world, right? People have been writing Blender.
31:0831 minutes, 8 secondsBlender is a 3D animation software.
31:1031 minutes, 10 secondsConnect it to uh Open Cloud or Claude or Cursor or whatever you can think of.
31:1531 minutes, 15 secondsIt's making 3D models for you. You can connect it to tally. Suddenly it can actually download the balance sheet change makes make edits and upload it.
31:2231 minutes, 22 secondsYou can connect it to um uh SAP and it can make those changes. So MCP basically becomes this uh wrapper which allows us
31:3031 minutes, 30 secondsto handle everything. So now the good part is businesses and developers can easily extend AI uh capabilities across various ecosystems and
31:3931 minutes, 39 secondsget more people out of the job right so that's what MCP was designed for is doing it really really good because now right from accounting software to the
31:4731 minutes, 47 secondssales call to uh customer support all that can be handled by AI and we we need less people now so we have been successfully designing tools to get rid
31:5631 minutes, 56 secondsof humans and this is literally the this is literally the um I'll save the root cause of all the job things that
32:0532 minutes, 5 secondsyou're thinking of uh that are going away. Uh simple use case of MCP. Think about how many functions are required to do something like this. Schedule a Zoom
32:1332 minutes, 13 secondsuh meeting with my team tomorrow at 10:00 a.m. Let's say you say something like that. Then in that case uh model need to recognize that you're looking for a request to uh schedule something.
32:2332 minutes, 23 secondsIt needs to call a standardized schedule function MCP compliant API. Maybe Zoom, maybe Google Meet. It needs to send a request to the Zoom API if you're using
32:3132 minutes, 31 secondsZoom. It receives the meeting link, confirms uh your meeting is scheduled and stuff. But look at the back in the background. What all needs to happen?
32:3932 minutes, 39 secondsSchedule a Zoom meeting with my team tomorrow at 10:00 a.m. It needs to look at the calendar. Make sure you are free at 10:00. Uh you're not supposed to be with your wife or husband or your
32:4832 minutes, 48 secondsin-laws, right? You need to make sure of that. Then it needs to uh schedule a zoom. Uh it says my team, who's your team? Needs to know that. fetch the
32:5632 minutes, 56 secondsdetails, email ids from some DB, put that in a zoom, send that uh get the request on your calendar also and structure everything and tell you yes
33:0433 minutes, 4 secondsI'm done. So you can think of multiple functions that are required to achieve this. This really enable true intelligence and automation. So MCP is
33:1133 minutes, 11 secondsliterally driving everything in the AI community especially on the agentic side. It's a very very simple thing but we still have to understand how it works and how can we write our own MCP tools.
33:2133 minutes, 21 secondsuh but moment this is done you can think about infinitely infinite possibilities for example uh think of a CNC machine right a CNC machine bought in 1990s or
33:3033 minutes, 30 seconds95 or maybe 2010 uh still 16 year old now in that case you want to automate that CNC machine now CNC machine is running Windows
33:3933 minutes, 39 secondsXP don't know you remember or not in that case it uh basically takes a uh
33:4533 minutes, 45 secondsG-code and runs the router to make some stuff how do we automate that in 2026 answer is MCP because MCP is literally
33:5433 minutes, 54 secondstaking that function and uh wrapping around with something and write that. So if you write a MCP wrapper, you can literally automate anything that you
34:0234 minutes, 2 secondswant. So the journey from basic LM to MCP is important for us to understand why MCP is important and why we need it.
34:0834 minutes, 8 secondsNow I'm predicting with MCP things like lang chain and other agent frameworks will CC exist and we are seeing that they're not as relevant today. You'll
34:1534 minutes, 15 secondsnot see any of the uh Googles or Anthropic or OpenAI ever using these frameworks. They just write the whole uh thing on their own. They believe that
34:2434 minutes, 24 secondsthey can write better faster. They understand the model nuances also. That is what makes them uh deliver at such a high speed. In fact, somebody released a
34:3234 minutes, 32 secondscalendar of what anthropic has released in uh just April.
34:4734 minutes, 47 secondswould be difficult to find because it was on
34:5734 minutes, 57 secondsTwitter, but literally every second day they've been launching one thing or the other.
35:0535 minutes, 5 secondsUh, this is still March. Open image in new tab.
35:1135 minutes, 11 secondsFebruary February again where you can see like I'm not even I
35:1935 minutes, 19 secondsdon't even want to open it. It's scary that every single day literally there's a new product release or new kind of stuff that keeps coming in.
35:3135 minutes, 31 secondsAll of that is MCP. Everything is linking back to some old function and speeding it up. Okay. Now before I
35:3935 minutes, 39 secondsproceed and now I'm going to show you how MCP works. Uh we'll have a break and uh I'm open to questions if you have any on the MCP and uh from there we'll see
35:4835 minutes, 48 secondshow it actually works. How do you write it? How do you wrap it around all right Pan?
35:5535 minutes, 55 secondsUh I have a question but just give me a second. Okay.
36:0636 minutes, 6 secondsHi Rohan. Yeah.
36:0736 minutes, 7 secondsUh I have some two questions. So um when an agent doesn't have any specific function, you said that we we can ask
36:1436 minutes, 14 secondsthe we can ask the LM itself to write that function, right? So is it possible that uh once it writes its own function
36:2336 minutes, 23 secondsdoes it take it to its uh function dictionary or something or is it just uh private to that particular call?
36:3236 minutes, 32 secondsOkay. Now uh not all agents do what I explained. Uh this was very specific to
36:3736 minutes, 37 secondsschool and it was uh in fact uh inspired from small LM.
36:4936 minutes, 49 secondsSo hugging phase came up with this concept that we don't need MCP at all.
36:5336 minutes, 53 secondsUh we will write a LLM that can actually just write its own code and proceed. And this strategy was picked in by us and we
37:0037 minutesintroduced that into our agent. So our approach to this pro problem is that if you do not have functions or if you do not have sometimes you actually need
37:0937 minutes, 9 secondssometimes you can communicate better in in code. So that's why this particular feature exists but the code runs in a sandbox and it's forgotten as soon as
37:1637 minutes, 16 secondsthe session is over. Uh we can remember it if we want to but the idea was that let's say there are 400 websites we want
37:2437 minutes, 24 secondsto scroll or we want to download from or you went to a website where there are 400 things that we need to download. In that case like going through 400 LM cost
37:3237 minutes, 32 secondsdoesn't make sense. So the code decides that LM decides that I can I can write a code for this and I can download all those files. So we allow the LLM to write a code but the code runs in a
37:4037 minutes, 40 secondssandbox because uh we do not want it to leak anything or run a command that is against our privacy or can harm the computer.
37:5037 minutes, 50 secondsOkay. Okay. Uh sorry I have one more question. Yeah.
37:5537 minutes, 55 secondsOkay. uh this is specific to uh any particular language. Say I gave some request saying that I write a story in some uh kungan language or something.
38:0638 minutes, 6 secondsOkay. So how does it start thinking about does it start thinking in first in that language or get the content in the
38:1338 minutes, 13 secondsbasic English or whichever language is prominent and then try to translate. How does it work?
38:1938 minutes, 19 secondsSo um the language most of the elements are trained on multil languages. The logic of thinking is separated from how the tokens are
38:2938 minutes, 29 secondsif you understand what I mean. It's not that it's thinking in English. It thinks in numbers and those numbers are then translated into the language of our choice.
38:3838 minutes, 38 secondsOkay. Got it. Thank you. Okay.
38:4238 minutes, 42 secondsUm Ron, we have an we have a use case wherein we have a third party integrated through an API and there are client uh
38:5138 minutes, 51 secondsuh proxies written in our code and it has been integrated in application. Now uh we are trying to integrate that with
38:5938 minutes, 59 secondsthe chat uh uh LLM chat uh Q&A sort of a flow where uh I can do it through a tool
39:0839 minutes, 8 secondscalling mechanism because those clients are already integrated or I can do it with the MCP I but then I have to write
39:1539 minutes, 15 secondsan MCP because that third party is not exposing their MCP. So what is the is is
39:2339 minutes, 23 secondsit I can do it through tool calling at right. So uh what is the best option to go or uh it is dependent on what use
39:3239 minutes, 32 secondscase how the situation is at that moment of time you can take that call.
39:3639 minutes, 36 secondsI really can't answer the question without looking because you're saying both at the same time. If you can do tool calling you already know the tool you know the inputs and outputs of that
39:4439 minutes, 44 secondstool. So you should just be able to write MCP on top of it. But the way you're describing it, do I need to write a MCP is what my question is.
39:5239 minutes, 52 secondsDo I do I need to? Depends on how many function calls you're talking about. Okay.
39:5739 minutes, 57 secondsIf it is 1 to 10, no. But if it is hundreds and others say 100%.
40:0240 minutes, 2 secondsSo does MCP facilitates um uh what uh what tools information is being in this prompt?
40:1240 minutes, 12 secondsNo, we we're going to talk about how that part is done. Okay. Fine. Okay. Okay.
40:1840 minutes, 18 secondsYeah. Hi. Um, so right now you're saying right that for a traditional API calls we had some problems integrating it
40:2540 minutes, 25 secondsbecause scaling it is a little bit of problem. Every API had their own authentication and that authentication served as a security layer right
40:3440 minutes, 34 secondsthat is still but now with MCP no that is still an MCP if that was the question. MCP still need aation layer.
40:4340 minutes, 43 secondsIt's not getting rid of that. It's getting rid of how the data is sent in and how the data is sent out. That's all.
40:5040 minutes, 50 secondsOkay. But then for different APIs, if you still have to pass the different authentications once, isn't it?
41:0041 minutesOkay. Once what? I did not catch that.
41:0341 minutes, 3 secondsWhat do you mean by once? And how is it different from previously?
41:0741 minutes, 7 secondsHow MCP standardized resources prompts and tools is the next topic. Okay. Okay. Okay. Well, Uh quick answer to you.
41:1541 minutes, 15 secondsThere are two MCP protocols. One is shake hand and then say I'm never going to meet you and other is uh shake hand and keep the hand and say no I'm not going to let you go. So it's a
41:2341 minutes, 23 secondscontinuous session. So we have two different kind of MCPS but we're going to talk about that. Okay. Okay. Okay.
41:3241 minutes, 32 secondsYeah. So two questions uh here. So when uh since the agent since the models are so good uh they have emerging capabilities why not we just uh give API
41:4141 minutes, 41 secondscontract to them and ask them to use it why do we need MCB as I said there are like billions and billions of functions written by humans
41:4941 minutes, 49 secondsin the last 40 years impossible of what you're saying the context will be just filled with different ways of responding
41:5641 minutes, 56 secondsthat's okay I mean u models can still configure they are not remember who wrote MCP anthropic itself the best coding model.
42:0542 minutes, 5 secondsSo it's not possible what you're saying just to explain a function is there to be able to use that function I need to read documentation of that function.
42:1542 minutes, 15 secondsYes. No. Yes.
42:1742 minutes, 17 secondsSo if you have a code where you have 40 functions I have to read documentation of those 40 functions before I use them versus
42:2542 minutes, 25 secondsyes the name of we can uh Mhm. So if you understand the difference
42:3242 minutes, 32 secondsin both like uh putting 1 million tokens in the context before I can start using code versus I know how I can use it.
42:4142 minutes, 41 secondsUh but in M MCP also we would need to write some uh description or comments in the uh functions right?
42:4742 minutes, 47 secondsYeah some versus many you're confusing some versus the book. It's like a pamphlet versus a book. Big difference.
42:5642 minutes, 56 secondsAnd on top of that the output structure is guaranteed. the output is guaranteed to follow a particular framework. So if
43:0243 minutes, 2 secondsthe if the API is throwing an error, MCP is going to capture the error properly and give it back to you. That is even even more important.
43:1143 minutes, 11 secondsOkay. Uh second question is uh most of the MCP servers that I see online like Figma or or a clashion they are uh built
43:2043 minutes, 20 secondsto be configured with some specific clients like cursor and you know clot.
43:2543 minutes, 25 secondsSo how do we use them in our applications? We'll we'll see that it's they may have written but there are a lot of open source also available that we can use. Uh MCP is literally a small wrapper on top on top of these.
43:3743 minutes, 37 secondsOkay.
43:3743 minutes, 37 secondsIn fact if you just check the open claw library uh any MCP you're thinking of should already be there.
43:4643 minutes, 46 secondsThank you Karthik two questions. First one is that u assuming you you gave an example of a
43:5343 minutes, 53 secondszoom call uh before that checking my own calendar right so what makes it decide that it has to first check my calendar and then it has to book an appointment
44:0244 minutes, 2 secondsso how does how does that level of optimism happen uh millions and millions of examples that LM keep reading online uh we
44:1044 minutes, 10 secondstalking about movie scripts we're talking about emails we're talking about conversations chats so build on top of experience that's why cursor was really
44:1944 minutes, 19 secondsgood and you can see that uh uh Elon is trying to buy cursor out and claw got so good because it has all the data it has seen those mistakes and is improving all
44:2744 minutes, 27 secondsthose mistakes so it would it won't do those mistakes at all. It's learning as we are actually prompting it. No, the reason I ask this question is that let's
44:3644 minutes, 36 secondssay in my company I have five or six business functions and they have to work it at least in some some level of order they so if I define these things as MCP
44:4444 minutes, 44 secondsfunctions how do I uh make sure that it's called sequencing or
44:5144 minutes, 51 secondsyou would you would not need to today AI is more powerful than a noble laureate uh there's a humanities last exam it has killed that those benchmarks also so
44:5944 minutes, 59 secondswith respect to IQ there is no question so if the flow follows a particular IQ IQ. It requires an IQ to be solved. That is not a problem. If your flow requires
45:0845 minutes, 8 secondssome very weird structuring that only on Wednesday 4 p.m. something can login, then we probably need to prompt it. Okay. Get that. Thank you.
45:1645 minutes, 16 secondsOkay. A.
45:1945 minutes, 19 secondsYeah. So is this MCP? So what I write is that you are explaining the two
45:2645 minutes, 26 secondsthings. So that could make us uh have a general feel for all the functions that are typically.
45:3445 minutes, 34 secondsSo is this MC specific to some languages or something? Because if let's say my some legacy code is in some other language basically.
45:4345 minutes, 43 secondsNot really. Uh it's there already in Typescript which covers all the JavaScript basically whole internet and then Python which covers all the other frameworks. If you have C++ then it
45:5245 minutes, 52 secondsneeds to be a sort of a Python wrapper which converts that and that is very easy to write. So literally not a problem. So Python can call any language
45:5945 minutes, 59 secondsin the world. JavaScript can also call any language in the world. So you will need to have two rappers in that case.
46:0446 minutes, 4 secondsOne that does the language conversion and on top of that we have MCP in both Typescript and Python. So but MCP is in in these two languages.
46:1346 minutes, 13 secondsCorrect. Correct. Okay. Shikant.
46:1846 minutes, 18 secondsYeah. Um my my question is like uh now we are seeing a rise in MCPS right and industry moving towards uh using this uh
46:2746 minutes, 27 secondsMCP as a way of calling and do do we think that uh uh the functions call will
46:3646 minutes, 36 secondslike no longer required and where exactly uh the enterprise is moving towards uh using this particular
46:4446 minutes, 44 secondsuh your your question is uh self-conlicting MCP is the way we call a function So how do I answer your question that will enterprise
46:5246 minutes, 52 secondswrite functions? MCP is a way to call a function. So maybe you need to restructure your question so I can understand better.
47:0147 minutes, 1 secondOkay. And and no the question actually came because I recently read that the BLEX is actually moving away from MCP.
47:0947 minutes, 9 secondsNow what exactly they they were actually doing like why they actually moving perfect city and uh
47:1747 minutes, 17 secondsuh perfect city is really good in always being in news. They tried to buy chrome at I think $56 billion while they themselves for $10 billion. So they know
47:2547 minutes, 25 secondshow to be in news. Unless anthropic tells us MCP is dead, I don't think it's going to be dead anytime soon.
47:3347 minutes, 33 secondsOkay. My last question would be like if I have to decide like uh if if I have to start simple then I have to start with
47:4047 minutes, 40 secondsjust functions with appropriate APIs and then if it is uh uh like you have more
47:4747 minutes, 47 secondscomplex complexity in nature then we have to go with an MCP service if it's available right that's correct okay
47:5447 minutes, 54 secondsokay sure so yes Rohan the whatever it is now showing in my in whatever you are sharing at
48:0348 minutes, 3 secondsthis moment the four actions with MCP the AI model right it's correct up till can you please help me sorry for
48:1048 minutes, 10 secondsmy uh incognition I'm still struggling to understand if these four are the basics task which I need to do as a part
48:1948 minutes, 19 secondsof agentic do don't you think that LLM in near future will be able to do this without any kind of MCP without any kind
48:2748 minutes, 27 secondsof extra tool within itself in LLM can this be done answer is no because let's Say I make a new zoom and call it boom.
48:3648 minutes, 36 secondsHow will LM use my tool if I do not access it like MCP?
48:4248 minutes, 42 secondsI just want you to realize that uh what I'm agreeing with what you're saying.
48:4748 minutes, 47 secondsCan LM solve it? Yes. How many iterations we want LM to solve it in is the question I'm throwing back at you.
48:5448 minutes, 54 secondsSo you tell me how many iterations LLM should use to solve a particular problem. One or 10?
49:0249 minutes, 2 secondsone.
49:0349 minutes, 3 secondsAnd how many tokens should it use? 100 or thousands? 100.
49:0749 minutes, 7 secondsThen you need MCP. That's the only difference.
49:1149 minutes, 11 secondsRLM strong enough to not use MCP and directly work with the uh any API we throw at them. Of course, they are. But
49:1949 minutes, 19 secondsthen they need to go do red document and then realize that oh 26th January it was changed and now we have to follow that part because it keeps on changing.
49:2749 minutes, 27 secondsRight? Who's going to tell the LM that the code has changed or the way we authenticate has changed now SSO is there now O key is also required now
49:3549 minutes, 35 secondssome PM file is required but P time has a different there are so many different things that are required just to recognize the request also
49:4249 minutes, 42 secondsokay I mean I'm still digesting but yeah but I I'm getting into it yes just try and understand that we want
49:5149 minutes, 51 secondsLM's life to also be easy like LM is strong enough doesn't mean we just use all our credits into uh just accessing one function. Let's make the function
50:0050 minutessimple is what they said. And if you just look at the Okay, just let me just show you. This is Blender.
50:1650 minutes, 16 secondsBlender is one of my favorite tools.
50:1850 minutes, 18 secondsThese are just some of the shortcuts for Blender. What is this Ro?
50:2450 minutes, 24 secondsBlender 3D animation tools. And if I press T, I get toolbar. If I press N, I get properties. If I press shift A, I can add any object. For X, delete.
50:3450 minutes, 34 secondsSo if you want our LM to use Blender, you're saying share the docu. And these are like 1% of all the features you're sh you're saying share the full
50:4150 minutes, 41 secondsdocumentation of thousands of pages and then make it use it. Just just think is this useful.
50:4850 minutes, 48 secondsGot right. For example, if I go here also and if I say control P, I have like tons of features here.
50:5750 minutes, 57 secondsSo, if you use Visual Studio or u Gemini on uh let's say anti-gravity, do you think we should focus on the whole documentation?
51:0651 minutes, 6 secondsNo. Right. Okay. Anerut.
51:1351 minutes, 13 secondsHello. So initially when charge is there like in the initial days we used to get more
51:2251 minutes, 22 secondsthan one or two responses and uh it used to ask which response is good. So is this all come does this all comes under
51:3051 minutes, 30 secondsR rf HF RHF that's correct okay and these days we cannot see any more questions about this uh I mean uh
51:3851 minutes, 38 secondsit is not taking active feedback about it about about this so is this already well trained no now uh unless you're talking to JPD
51:4651 minutes, 46 secondsfor long you're not going to see that because now they're testing long uh horizon context so for short things it doesn't do that anymore but I keep
51:5551 minutes, 55 secondsseeing if you continue a chat for 20 30 times you're going to still see that actually throws in your model.
52:0152 minutes, 1 secondOkay. So in the next topic uh we are going to learn about how MCP is allowing AI to interact seamlessly. Right. Correct.
52:1052 minutes, 10 secondsOkay. Thank you.
52:1152 minutes, 11 secondsSA did I miss you? Your hand is still up.
52:1352 minutes, 13 secondsUh no problem. Uh Rohan. Hi. Can you hear me? Yeah.
52:1752 minutes, 17 secondsYeah. Thank you. So my question is um you you have given a zoom meeting example. So um for example I have a scenario here uh for the commerce
52:2552 minutes, 25 secondswebsite the security detections everything will be made by my security software. So that's also website for me.
52:3152 minutes, 31 secondsSo every month I have to do some uh detections I have to ignore detection or I have to act on the detection that's on separate security sites. Now I have some
52:4052 minutes, 40 secondsdata means u the data which that these issues can be ignored. These issues cannot be ignored for something like
52:4752 minutes, 47 secondsthat. Now if I interact if I want to interact to a site using MCP as you said and I wanted to do this work automated I want to automatic uh automate this work.
52:5752 minutes, 57 secondsNow is there any my question is um is there any way uh can I know can I learn that this action can be done through MCP
53:0653 minutes, 6 secondsthis action is restricted by that site through MCP dos and don'ts or even before I jump into my development or
53:1353 minutes, 13 secondssomething may I know what it offers uh now the question is uh general what the
53:2053 minutes, 20 secondssite offers through MCP means I can only read or I can act on it edited uh the crowd operations which you said we we'll see that the moment we connect
53:2853 minutes, 28 secondsto any MCP uh app we have a tool set which tells us these are the only tools that are available outside that we can't access anything
53:3553 minutes, 35 secondsso before acting on it I can learn what I can do I can design I can design my work and uh then only I can jump into my development maybe
53:4353 minutes, 43 secondscorrect any MCP yeah that's the first step okay
53:5053 minutes, 50 secondsyes can you please explain the line I'm predicting MCP this one please which one the on the screen I'm predicting that there must be things
53:5953 minutes, 59 secondslike lang and aentic framework will cease to exist. I don't know much about lang and aentic framework so don't even ask there are many other
54:0754 minutes, 7 secondsframeworks that try to integrate every single application manually lang chain and other engineic frameworks are like there was a lang graph then there's
54:1454 minutes, 14 secondscrew.ai AI very famous in last year. Uh their key feature was that we have integrated these 400 applications. MCV
54:2154 minutes, 21 secondskilled all of that. So don't even know try and know what they are. Clear about this.
54:2954 minutes, 29 secondsYeah. So all of these are killed because of MCP and their feature was that okay we have multi- aent platform we have integrated
54:3754 minutes, 37 secondseverything and blah blah blah. Moment MC MCP came in all that was gone.
54:4554 minutes, 45 secondsSo a framework essentially binds us to use them. uh if you use crew then you have access to anthropic access to Google cloud IBM I don't know HubSpot
54:5454 minutes, 54 secondsright uh slack all of that is MCP now okay sorry
55:0155 minutes, 1 seconduh just one just to validate I understand is API written in a standard format by
55:0955 minutes, 9 secondsevery tool I interpret this thing uh please
55:1655 minutes, 16 secondsMCP is Basically uh API is written in a standard format.
55:2255 minutes, 22 secondsMCP is basically a wrapper to get a specific input get a specific output for any function that is written inside.
55:3155 minutes, 31 secondsSo no comparison with API that's the world.
55:3555 minutes, 35 secondsNo MCP is API but it has a fixed input fixed output. So any other API can be modified internally to follow that fixed input fixed output schema.
55:4455 minutes, 44 secondsThank you. That's okay. AJ yeah sorry sorry
55:5355 minutes, 53 secondsuh so I think my question is the same previous question uh it's kind of a the tool we we are writing the tool like
56:0056 minuteslast uh uh session we uh talked about and learn right so we are just uh
56:0656 minutes, 6 secondswrapping up our tool call with some MCT like the red tools we are doing correct so that we make one request
56:1556 minutes, 15 secondsto the tool call and the output of that to call it formatted and send exactly kind of a protocol am I right
56:2256 minutes, 22 secondsyes exactly okay so what is that mean the response I understand what is the request he'll be
56:2956 minutes, 29 secondsdoing how to call and all like suppose I have written my own
56:3656 minutes, 36 secondsfunction okay method so response I can understand he can format the response of the method call
56:4356 minutes, 43 secondsbut What will be the input mean how will you format the input like what is the argument and how it will be called like that it will be formatted or
56:5156 minutes, 51 secondsthat will also be formatted. Yes. Let's say you're sending text but we're expecting JSON a particular key and a value. So MCP will take care of that.
56:5956 minutes, 59 secondsSo that that input and output we need to tell MCP or MCP will he will do by himself.
57:0657 minutes, 6 secondsWho's using MCP? LLM or you uh LLM is using so okay LLM will have formal data.
57:1457 minutes, 14 secondsOkay.
57:1557 minutes, 15 secondsOkay. VJ Ron, I didn't I mean this is in line with some of what the earlier questions.
57:2157 minutes, 21 secondsI don't understand what's so innovative about this, right? Like in the sense there's nothing innovative about it.
57:2657 minutes, 26 secondsIt's just monopoly power of one company saying that we are going to do business in MCB. That's it. It's it's a open format open for all.
57:3357 minutes, 33 secondsIt's not a proprietary format for anyone. It's just like USB. It's like this is how we are going to communicate and the world let's please agree on it.
57:3957 minutes, 39 secondsAnd the world saw that this was required and they agreed on it. That's all.
57:4257 minutes, 42 secondsYeah. So that this the followup question I had was in your Blender example, right? Let's say hypothetically Blender didn't want to play ball, right? Blender does not want to make you allow LLMs or
57:5157 minutes, 51 secondsagents or whatever you call this AI to access me, right? The clever way to go about doing that is to force Blender to learn all of your shortcuts and you're
57:5957 minutes, 59 secondsnot able to tell if the shortcut originated from a human key press or an agent's key press. Right? This is the nice way of going ahead and doing like
58:0758 minutes, 7 secondsessentially Roen and I speak different languages. Both of us agreed to do business in English and that's it. That's the only thing that's innovative here.
58:1458 minutes, 14 secondsThat's the only thing that is innovative here. The structure. Got it. Yeah. Thank you. Okay. Reina.
58:2058 minutes, 20 secondsYeah. Uh so my question is Rahman that MCP is a separate service or a server that LLM is going to interact with to
58:2758 minutes, 27 secondsachieve these calls. Say suppose like you have given the example earlier a new meeting application has come in the
58:3458 minutes, 34 secondsmarket. uh so for the APIs for that new application uh who should be making it MCP compliant that application has to
58:4358 minutes, 43 secondstake care or the company who is providing the LLM will take care like cloud or so what what no no definitely not cloud or Gemini they don't don't even know the
58:5158 minutes, 51 secondsAPIs and the functions that are there so what happened initially was uh moment MCB came in lot of companies played ball
58:5858 minutes, 58 secondsand wrote their own MCP MC writing MCP client is very simple as I said yeah all you have to do is to go on top of function write that tool, right? That's
59:0659 minutes, 6 secondsthe simplest possible code change anyone can do. But open open source community came in and they wrote MCP for everything because nearly every single
59:1559 minutes, 15 secondsapplication we can think of has a programmatic access. We can access Gmail through programs. We can access Google cloud or Google uh GCP or our uh Google
59:2459 minutes, 24 secondsDrive through commands already. So all they had to do was to write a MCP and uh no you can't stop it. If a company has
59:3159 minutes, 31 secondswritten the API and they provided API to people uh to access anyone can write MCP on top of it and just integrate. So you just can't stop it. So company just wrote themselves.
59:4159 minutes, 41 secondsBut it's not the job of Anthropic or Google.
59:4459 minutes, 44 secondsUh so how will my LLM know about these MCPS that are available? We are going to see a look at it next.
59:5359 minutes, 53 secondsThank you. Okay. Karthik.
59:5559 minutes, 55 secondsHey, what is this open cloud which everyone is thinking about? What does it do? Is it similar as input?
1:00:021 hour, 2 secondsUh very long answer. Imagine charge GPD with access to your Gmail, Google calendar, your banking details and etc.
1:00:091 hour, 9 secondsand can email and uh chat with you on Telegram, on Slack and other stuff.
1:00:151 hour, 15 secondsBut that essentially is MCP that is not MCP. That is how it becomes powerful. Without MCP that's not possible. But that is not MCP.
1:00:251 hour, 25 secondsYeah. No, I mean so so that uses MCP as a protocol. That's correct. the orchestra program. Yes, that's correct.
1:00:311 hour, 31 secondsOkay. And one more question like suppose let's say I have both scheduling app. I have a Google meet and also zoom right and uh yeah mctc is different for these
1:00:401 hour, 40 secondstwo. Uh with my program so when I ask it to schedule it so how do I how does it decide which one it has to go and uh schedule on?
1:00:481 hour, 48 secondsYou would have had to have your preferences or it would have seen that you already using Google meet or your people uh you want to talk to they have Google meet. It's a very personal question.
1:00:581 hour, 58 secondsOkay. No. So I mean so it's there somewhere in the context. That's how it decides. Yeah. Okay. Thank you. Okay. Praep.
1:01:111 hour, 1 minute, 11 secondsHi. Hello. Go ahead.
1:01:141 hour, 1 minute, 14 secondsYeah. Hi. Uh actually in our organization we are already using MCPs like uh where we explore the MCP options
1:01:221 hour, 1 minute, 22 secondsbecause we have different systems having their own way of implementing the APIs to connect those APIs to the LLM we use
1:01:301 hour, 1 minute, 30 secondsthe MCP as a as a hub layer right so I have a question actually like we are running into issues like uh if an
1:01:381 hour, 1 minute, 38 secondsexample the API payload is high right where it's I mean because the JSON response whatever the MCP is returning
1:01:451 hour, 1 minute, 45 secondsthat we are injecting into the LLM and where we are seeing the issue is like always LLM the context bloating issue is happening is there a way better way that
1:01:541 hour, 1 minute, 54 secondswe can handle this situation uh Roman any suggestion product uh yes but that's a part of the next next uh next sequence that is coming in
1:02:031 hour, 2 minutes, 3 secondsbut it's your responsibility to reduce that uh context bloat okay uh so what we try to do is just uh
1:02:131 hour, 2 minutes, 13 secondsuh instead of JSON convert into the markdown by extracting the required phase but still we we see some uh I mean
1:02:201 hour, 2 minutes, 20 secondsperformance issues so of checking any better solution available for this move to opus 4.7
1:02:281 hour, 2 minutes, 28 secondsokay but there are other ways we'll see how uh cloud code handles and in fact um by
1:02:351 hour, 2 minutes, 35 secondsthe I think 10th or 11th session when we start reviewing what cloud code also does internally we'll have much better idea you need to collapse the context
1:02:421 hour, 2 minutes, 42 secondsalso we need to throw away some of the things that are not required or maybe rewrite the uh the data in such a way that it's not taking everything.
1:02:511 hour, 2 minutes, 51 secondsOkay.
1:02:521 hour, 2 minutes, 52 secondsOkay. Ganesh uh and more question uh just uh uh do we have in this course do we also have a scope I mean scope of discussion for MCP
1:03:011 hour, 3 minutes, 1 secondapps which is latest in the MCP where we can dynamically render the screens on the chat even uh we are going to do that today. Uh
1:03:101 hour, 3 minutes, 10 secondsokay Ganesh one sorry line by line Ganesh yeah yeah
1:03:191 hour, 3 minutes, 19 secondsat some point in time will MCP replaces finetuning uh no no no MCP is access to the world finetuning is how model becomes better
1:03:271 hour, 3 minutes, 27 secondsboth are different correct say for example if I want model to be tuned to my no
1:03:331 hour, 3 minutes, 33 secondsdata wrong idea again because models are really good in in context learning and your MCP The tools may change in future so you'll have to retrain the very expensive.
1:03:431 hour, 3 minutes, 43 secondsOkay. Yeah. Yeah. Okay. You still have a question?
1:03:461 hour, 3 minutes, 46 secondsYeah. Um, so I assume I have a legacy Java API to find restaurants around me and today consumers uh build the request payload manually.
1:03:551 hour, 3 minutes, 55 secondsUh, if I want an MCP compatible clients like whoever is calling me to just use natural language. Um, what should change
1:04:031 hour, 4 minutes, 3 secondslike from my side versus the client side?
1:04:051 hour, 4 minutes, 5 secondsJust just MCP server just write MCP server on top.
1:04:091 hour, 4 minutes, 9 secondsAnd if I don't want to make any changes as a provider, even the clients can do something on their side to make it MC.
1:04:161 hour, 4 minutes, 16 secondsIf your API is open, yes, not open source. Open. Yes. Okay. Okay. Ashi.
1:04:231 hour, 4 minutes, 23 secondsNo, it's their own. So, so is MCP also leveraged for agent to agent communication? Yes, it's sort of a backbone for that.
1:04:301 hour, 4 minutes, 30 secondsWe're going to cover that.
1:04:321 hour, 4 minutes, 32 secondsAll right, sir. Thank you. Okay. Kanga kangala.
1:04:401 hour, 4 minutes, 40 secondsKungla Karthik uh hello can you hear me?
1:04:431 hour, 4 minutes, 43 secondsYeah yeah uh yeah just I'm trying to connect the uh last session to this session. So like last session we have
1:04:501 hour, 4 minutes, 50 secondswritten the functions right. So how uh can you give an example of how MCP will uh differentiate from the last session
1:04:591 hour, 4 minutes, 59 secondslike we Yes. Last session last session. Last session. Last session. Can you mute anyone?
1:05:061 hour, 5 minutes, 6 secondsUh sorry can you go on mute? Okay. Yeah.
1:05:091 hour, 5 minutes, 9 secondsOkay. Last session we wrote our functions and we wrote our functions the way we wanted and we said this is how I want the output. This is how I'm going to provide the output. Right? Uh this is
1:05:161 hour, 5 minutes, 16 secondshow I want the input. This is how I will provide the output. So that's the way world was writing it. Now moment we think about integrating millions of
1:05:251 hour, 5 minutes, 25 secondsapplication thousands of features and other stuff moment that happens MCP is required. So what we saw was the world before MCP. Today we are seeing how that
1:05:331 hour, 5 minutes, 33 secondsshould have been written. So we're going to rewrite the function that we wrote in the last session but using MCP today.
1:05:381 hour, 5 minutes, 38 secondsThat's the real answer that we're making the life of the LM to be easier. Again going back to the same thing. Can LM read every single function for a particular application and solve a
1:05:461 hour, 5 minutes, 46 secondsproblem? Answer is yes. But you're building a context and it will just not work longer. We want our LMS to work for days. Now if that has to be done, we
1:05:541 hour, 5 minutes, 54 secondshave to use something like MCP. So it is just not remembering. Okay. Uh uh the documentation will have literally everything, right? or you're going to say no I will fine-tune the
1:06:031 hour, 6 minutes, 3 secondsdocumentation itself. So what you're going to do if you try and let's say your organization has thousand functions right and you want to uh use LM you're
1:06:101 hour, 6 minutes, 10 secondswhat you're going to see is you're going to throw all the thousand function and it's going to come back and give you worse and worse answer then you're going to realize oh my documentation is bad
1:06:181 hour, 6 minutes, 18 secondswhy don't I write my documentation in better way so you're going to write a documentation is better way LM will improve that when then you're going to see that it fails for some function it's
1:06:261 hour, 6 minutes, 26 secondsreally good for some of the function then you're going to realize it's good for that function because input was structured output was structured here the input was slightly weird output was slightly weird you're going to say okay
1:06:341 hour, 6 minutes, 34 secondslet me change my API to make sure the element performed better and that cycle is something that MCP has fixed it said
1:06:411 hour, 6 minutes, 41 secondsthat doesn't matter how your legacy API was just make them into a MCP tool and the uh protocol will take care the input
1:06:491 hour, 6 minutes, 49 secondsis structured and output is always structured so we don't have to make changes on the API level that is what MCP has done so last time we wrote a API literally list of functions today we're
1:06:571 hour, 6 minutes, 57 secondsconverting those APIs into MCP so it usable by everyone so you can actually share your own file with the world and they can also use it. Uh one more
1:07:061 hour, 7 minutes, 6 secondsfollowup to uh Ran like whenever we give prompt to like a cursor right it would say cursor or VS code it would say that
1:07:141 hour, 7 minutes, 14 secondsMCP server starting what is it like get connection shows we are going to see that today okay okay Samra
1:07:241 hour, 7 minutes, 24 secondsquestion so you mentioned about documentation so uh can LLM optimize the documentation
1:07:331 hour, 7 minutes, 33 secondsbased on looking at the any API code or service that we wrote and then we write a MCP on top of it. Is that better?
1:07:431 hour, 7 minutes, 43 secondsThat that is how people will write the MCP for any of their own existing API. Yes. Okay. Thank you.
1:07:521 hour, 7 minutes, 52 secondsYeah. You keep saying uh MCP will take care of it means you just convert your API to uh use that keyword
1:08:031 hour, 8 minutes, 3 secondstool. Yeah, MCP will take care means what I mean you will see that in 2 minutes.
1:08:091 hour, 8 minutes, 9 secondsAll right. So now let's see how we actually use MCP. Now let's see how MCP standardizes what all
1:08:171 hour, 8 minutes, 17 secondswe said we have resources and prompts and tools and the best way to actually do that is going to be to actually run one. So I'm opening a new terminal. I'm
1:08:241 hour, 8 minutes, 24 secondsgoing to be running this file which is called example MCP server. Let's zoom in a bit and let's see what it does. So
1:08:321 hour, 8 minutes, 32 secondsit's a crossplatform NCV server. Uh there's a teaching example. Uh inside we'll have tools some other function that allow for file CRUD basically read,
1:08:411 hour, 8 minutes, 41 secondswrite, edit and list and delete. We have few resources that can be fetched by the model. HTTP fetch to reach outside the
1:08:481 hour, 8 minutes, 48 secondsworld and get some let's say news or website. Uh SQLite CRUD to edit the data in a particular SQLite database that we
1:08:561 hour, 8 minutes, 56 secondsmay have. A shell runner a dangerous tool guarded by the allow list. Uh this is something where uh your LM is asking
1:09:031 hour, 9 minutes, 3 secondsto do something on your command prompt or your terminal. Uh GUI automation crossplatform uh tool where you can actually go and click a particular u
1:09:121 hour, 9 minutes, 12 secondswebsite button or something on your desktop. Also image tool that actually returns a PNG and then prompts. Now we can MCP can actually provide prompts
1:09:201 hour, 9 minutes, 20 secondsalso a prompt example to give a better idea of how to do a particular thing. Now we are going to be using stdio.
1:09:271 hour, 9 minutes, 27 secondsstdio.io is uh use the MCP tool once and then close the connection. Right? So here uh these these MCP tools are once
1:09:361 hour, 9 minutes, 36 secondsin a while usage where you just read a file and then be done with it. So you do not need a constant access to that. But there's going to be another kind of uh
1:09:451 hour, 9 minutes, 45 secondsMCP server where we want to continue the connection. For example, you want to have a constant connection with LLM on a telegram. In that case, you may need a constant connection.
1:09:551 hour, 9 minutes, 55 secondsWe're not covering that today. that we'll cover in the next session. Okay.
1:09:591 hour, 9 minutes, 59 secondsNow, simplest way to run is Python example MCP server, which is what I'm going to be doing now. But I'm going to be running this on uh with this command, which called MCP example MCP server. py.
1:10:111 hour, 10 minutes, 11 secondsThis is the command you're going to be running to run the server and let the LM use the tools. Today, I'm not going to do that part first. I'm going to show
1:10:191 hour, 10 minutes, 19 secondsyou the developer environment in which we can uh play with the MCP server manually, right, without the LM. So we should also be able to see what is
1:10:261 hour, 10 minutes, 26 secondshappening what are the tools that are available how will the LLM actually see the input and output and other stuff.
1:10:311 hour, 10 minutes, 31 secondsNow before we do all of that make sure that you're installing this MCP CLI which is command line interface then pillow for image features function that
1:10:391 hour, 10 minutes, 39 secondsI have written uh request and pi autogy in case you are interested to automate some of your desktop stuff. Okay. So
1:10:471 hour, 10 minutes, 47 secondssome of the initial prayers to the gods and then we have the pill also reaching there. The name of the server that is written is called teaching server. Now
1:10:551 hour, 10 minutes, 55 secondsthis is a sandbox. Sandbox essentially is literally a folder. U the MCP server or LM is write is allowed to write a
1:11:031 hour, 11 minutes, 3 secondsfunction only in that folder and whatever is inside that folder will be accessed. So that's sort of a contization. So one of the first uh time
1:11:111 hour, 11 minutes, 11 secondsyou're seeing how do we make sure the environment is secure and it's not reading any file from the computer right and sometimes you're going to see that when you're working with cursor or
1:11:181 hour, 11 minutes, 18 secondsgemini anti-gravity is going to say I don't have access to read that file can you give me that access so every time it asks for the access because the sandbox
1:11:261 hour, 11 minutes, 26 secondsis only that folder the folder in which you're writing the code that this is very similar to that okay so here is add
1:11:331 hour, 11 minutes, 33 secondsfunction that we also wrote in last session all I had to do to convert this into MCP tool is to just write at mcbp dot tool that's all now and you're
1:11:431 hour, 11 minutes, 43 secondsasking me that why should I write MCP will be difficult no just go in the Python file whatever function you have
1:11:501 hour, 11 minutes, 50 secondson top just write at MCP tool and that's all that's the Python decorator we covered in last class and today also right so now at MCP tool just converts
1:11:581 hour, 11 minutes, 58 secondsthat function into an MCP so all the function that you're going to see in fact control D if I do you're going to see all the functions that I need to
1:12:051 hour, 12 minutes, 5 secondsconvert into uh an MCP tool just go on top of the functions Just write at MCP tool. So we have add square root
1:12:111 hour, 12 minutes, 11 secondsfactorial Fibonacci. Now these are CRUD list files. What are the files available to me that I can work with or edit?
1:12:181 hour, 12 minutes, 18 secondsMaybe the folder is also empty. Read a file to read a particular file. Write a file to write a particular file. And again that's where the sandbox is required. Only edit things in that
1:12:271 hour, 12 minutes, 27 secondsparticular folder. By the way uh uh these four along with some eight functions is what clot code or cursor or anti-gravity is. So moment you have
1:12:351 hour, 12 minutes, 35 secondsthese 12 functions done, you can write the whole thing on your own. Right? And cloud code anyways was uh command line interface. You don't need a GOI as well.
1:12:431 hour, 12 minutes, 43 secondsRight? That's why uh simple but we'll see how do we use it. Then we have edit file editing a particular file. So here
1:12:511 hour, 12 minutes, 51 secondsand here we have a delete file. So you see that here we have simple features list files in the folder read a particular file write a particular file
1:12:581 hour, 12 minutes, 58 secondsedit a particular file and then delete a particular file. But uh anti-gravity and clot code and cursor will have more functions. they'll have go in a go in a
1:13:071 hour, 13 minutes, 7 secondsfolder or go in a file look for a particular line change it or go below that particular function write something there or go on top of particular
1:13:141 hour, 13 minutes, 14 secondsfunction write a so it has more different uh like targeted edits also so those are some additional command that we can add to make it a full feature
1:13:221 hour, 13 minutes, 22 secondscode editor okay then what are other tools then we have uh mcpresources these are the things that we can provide
1:13:291 hour, 13 minutes, 29 secondsresources are like files they are like text they're like keys they're like some structured output that may be required for just display they don't do anything
1:13:371 hour, 13 minutes, 37 secondsthey just provide them as URI which is unique resource identifier read only basically you can read some stuff and
1:13:451 hour, 13 minutes, 45 secondsprovide so we have these as well then here again a tool fetch a URL so if now I ask my LM to go on a particular website and get the data I can use this
1:13:531 hour, 13 minutes, 53 secondsparticular tool then this is a DB that we made a simple SQLite and uh let me in the meantime run an Olama also because I'll be using
1:14:021 hour, 14 minutes, 2 secondsit let me say hi to this guy Okay, then we have a note add, a note list,
1:14:091 hour, 14 minutes, 9 secondsnote update, note delete, right? So, literally any function you can think of command. So, it's going to run on a command prompt. But again, just write MCP uh tool on top and it's going to give you all the features. All right.
1:14:211 hour, 14 minutes, 21 secondsSo, as I told you, there are two ways of running it. One way is to run the MCP server, which is going to be Python.
1:14:261 hour, 14 minutes, 26 secondsThis fe you need to run uh when your LM is running. So uh in future when we're going to be writing our agent it will
1:14:331 hour, 14 minutes, 33 secondshave a process of booting up right just like a your computer boots we'll have a process of our agent also booting up.
1:14:391 hour, 14 minutes, 39 secondsNow one of the first few step is going to be that MCB server has boot booted properly because if the function is not available your agent is going to be
1:14:491 hour, 14 minutes, 49 secondsdo later on right so there's going to be a process so this is something that our code will automatically do in future which is python example mcbcbs server.py
1:14:581 hour, 14 minutes, 58 secondspy it's just going to say starting that's all it doesn't show anything right after that the llm would have booted up but we don't want this right
1:15:051 hour, 15 minutes, 5 secondsnow so I've just killed it what we're going to be doing today is mcpde dev example
1:15:121 hour, 15 minutes, 12 secondsnow this is going to open a dev server for me and it is also going to be opening a particular URL for me or web
1:15:191 hour, 15 minutes, 19 secondspage for me which has opened on my left screen so I'm just going to move it here this is how the dev server of mcp looks
1:15:271 hour, 15 minutes, 27 secondsNow going back here now when you are developing u what I'm about to say was true last year not this year when you are developing
1:15:361 hour, 15 minutes, 36 secondsMCP server and it crashes there's some uh you'll be stuck on understanding what do I do so this is what you should be doing basically open the browser and go
1:15:441 hour, 15 minutes, 44 secondsand check there but we are in 2026 April so plot code would have done everything for you okay so what we're going to do is go back to our server and click
1:15:521 hour, 15 minutes, 52 secondsconnect here now this browser page is getting connected to the MCP server the connection is done if you go back here you'll see that created client create
1:16:011 hour, 16 minutes, 1 secondtransport and something is happening in back end now we are using stdio as I said stdio is make connection once and
1:16:081 hour, 16 minutes, 8 secondsthen disconnect so moment I uh basically kill that particular function on my end it would have disconnected the session with the mcp server also so some someone
1:16:161 hour, 16 minutes, 16 secondselse can take that connection if you were using s or streamable http then the connection is live right from the streamable you can understand what these
1:16:251 hour, 16 minutes, 25 secondstwo might be but we're going to look that later on. Okay. Now we have resources, we have prompts, we have tools, we have apps, ping, sampling,
1:16:331 hour, 16 minutes, 33 secondselicitation, roots, o metadata. We're only going to focus on tool today. So now when when I click on tool, you're going to see this UI. Nothing special about it.
1:16:431 hour, 16 minutes, 43 secondsBut if I'll click on list tools, you're going to see that something happened here. So initialization was happened at the back end. This all of this happened.
1:16:531 hour, 16 minutes, 53 secondsBut look at this particular stuff method list tools. So when our LLM connects to the MCP or whenever our program connects
1:17:011 hour, 17 minutes, 1 secondto the MCP, first thing we're going to do is to run this particular command called tool call or list the tools.
1:17:071 hour, 17 minutes, 7 secondsMoment we list the tools the application or the functions that are available in that MCP are listed immediately. So we get all the list of all the function
1:17:151 hour, 17 minutes, 15 secondsthat we saw there. Right? So if you go back here and if you remember the add function or the list function factorial function we just wrote add MCP tool on
1:17:221 hour, 17 minutes, 22 secondstop and that came here here when I click this the UI will change okay now see what we have here add to number A is
1:17:301 hour, 17 minutes, 30 secondsfloat B is float and output is float and add that's that's all and we have a dock string here add two numbers and look what happened here add two numbers
1:17:381 hour, 17 minutes, 38 secondsautomatically got pulled A B here we are saying is read only destructive so there's some other details that are available for the LM now a I can write
1:17:461 hour, 17 minutes, 46 secondslet's say 45 B I can write let's say 23 right and this is the data in which the output is going to be sent here you're
1:17:551 hour, 17 minutes, 55 secondsseeing what MCB looks like right so output schema well definfined for the LM so LM know the input schema which is this function and output schema this is
1:18:031 hour, 18 minutes, 3 secondshow the output look like so when it calls a tool it gets output it knows oh my answer is supposed to be here at a zero right now if I click run tool
1:18:131 hour, 18 minutes, 13 secondssomething will change here also this is the output that would have been sent to the so let's take it up this is the most
1:18:211 hour, 18 minutes, 21 secondsimportant part I wanted to look at so when we call a function using MCP all of this happened this is how the tool was
1:18:291 hour, 18 minutes, 29 secondsrequested right so what how will your lm call a particular tool lm will say method tools call in the parameter is
1:18:361 hour, 18 minutes, 36 secondsgoing to say name add name of the function arguments are a4 b23 and progress token is not relevant for us and the response it is going to get in
1:18:451 hour, 18 minutes, 45 secondsthe Next iteration is going to be type is text and text is 68.0. Now this is something that is still improving uh this particular part.
1:18:541 hour, 18 minutes, 54 secondsSometimes we don't want text. Sometimes we actually want let's say a number or a boolean or some let's say JSON or image.
1:19:001 hour, 19 minutesThat part is improving a lot. But this is literally what happens in MCP. So every function that you can think of every legacy API that you can think of
1:19:091 hour, 19 minutes, 9 secondswill be called like this tool call. I'm calling it tool. name of the function literally just that arguments how the
1:19:161 hour, 19 minutes, 16 secondsargument need to be presented and the protocol is defined like this that you're going to get your content of type
1:19:221 hour, 19 minutes, 22 secondszero text that's all that's all MCP is right so if you go back here you're going to see that some post message received so nothing happens on the
1:19:311 hour, 19 minutes, 31 secondsserver on the command prompt everything is going to happen here now let's look at sqrt square root of what let's say square root of 36 because you can
1:19:381 hour, 19 minutes, 38 secondscalculate that and here you're going to content result six that's the response
1:19:461 hour, 19 minutes, 46 secondsthat we get now factorial let's say we want to calculate factorial of five you're going to see output is 120 then
1:19:551 hour, 19 minutes, 55 secondslet's say Fibonacci Fibonacci series for let's say six numbers these are six numbers you can see always
1:20:031 hour, 20 minutes, 3 secondsthe output is always in the result format in a particular way right so LMS will never get confused on what is expected subdirectory with subdirectory
1:20:111 hour, 20 minutes, 11 secondsI only have as I told you I only have this so I'm going to uh copy
1:20:181 hour, 20 minutes, 18 secondspath maybe I need to give a yes it's going to see that there are only three files in that folder so if I
1:20:261 hour, 20 minutes, 26 secondsgo in sandbox you can see greeting txt nodes db and sample txt that's the result I'm getting this is how anti-gravity works what are the commands
1:20:341 hour, 20 minutes, 34 secondswhat are the files that I have in that particular folder now read file which file do I want to read I want to read
1:20:411 hour, 20 minutes, 41 secondslet's say greeting.txt txt. So, right click, copy path
1:20:491 hour, 20 minutes, 49 secondssuccess. It says hyon. So, if I go inside that file, it's going to say hyon. Then read a file. Write a file.
1:20:561 hour, 20 minutes, 56 secondsPath. Where do you want to write? I want to write here. And reading greeting. Uh let's say sleeping.
1:21:041 hour, 21 minutes, 4 secondsI am something like that. and done. Now if I
1:21:121 hour, 21 minutes, 12 secondsgo back here, you're going to see sleeping. So MCP is sort of make sure the input and output is always same. You can see result, right? So the way we
1:21:211 hour, 21 minutes, 21 secondscall and the way we get the result becomes same for any function. And you can think of just in this case, right?
1:21:281 hour, 21 minutes, 28 secondsExample, if you go back just in this example, how many different ways are there to call here? I need to provide two floats. Here I need to provide one float. I need to provide one integer and
1:21:371 hour, 21 minutes, 37 secondsin so all the integer conversion, float conversion, text conversion was taken care by MCP because LM can only give what text right lm output is always
1:21:461 hour, 21 minutes, 46 secondstext. Someone has to interpret that as a text as an image and other stuff. MCP is going to handle that for us. And functions can return anything. Function can return float, it can return decimal,
1:21:551 hour, 21 minutes, 55 secondsit can return a a bite, it can return an image, it can return anything that is possible. But what can LLM take? LM can
1:22:021 hour, 22 minutes, 2 secondsonly take text. MCP is going to convert that into text. It can take images also but that is out of context. But if it is being sent a image then say we need uh
1:22:101 hour, 22 minutes, 10 secondsthe LM needs to be told that is actually being sent a text right let's continue forward we wrote the file edit the file now which file we need to edit so let's
1:22:191 hour, 22 minutes, 19 secondsgo and edit this what is the old uh stuff there it said hi Rohan I believe it needs to be correct otherwise it's going to just hi Rohan and I want to
1:22:271 hour, 22 minutes, 27 secondsconvert that into hi everyone right why only hi me run tool success and if you go back here you're
1:22:351 hour, 22 minutes, 35 secondsgoing to see hi everyone so That's how literally what MCP works. So I can go and change. Let me
1:22:441 hour, 22 minutes, 44 secondsmove my coordinate. Uh my screen by the way is 3 to I don't even know what is my
1:22:501 hour, 22 minutes, 50 secondsscreen dimension. Let's say 4500 X 4500 and Y uh let's say 300.
1:23:051 hour, 23 minutes, 5 secondsYou saw it went somewhere else. Uh, 1500.
1:23:121 hour, 23 minutes, 12 secondsOh, now it is on this screen. Uh, see I'm on Mac, right? So, I have a wider screen. So, I need to understand where
1:23:201 hour, 23 minutes, 20 secondsthis is how we automate stuff. So, go there, click, go there, click, go there, click. You can now automate the you can now in fact if you have a CNC machine
1:23:301 hour, 23 minutes, 30 secondsright where uh you don't even have the API it's just a old display of button that someone needs to go and do a mouse
1:23:381 hour, 23 minutes, 38 secondsclick you can automate that now take a screen send it to claw uh send it to uh let's say opus 4.7 and say that can you
1:23:461 hour, 23 minutes, 46 secondsstart a CNC machine it's going to see CNC machine that's the coordinate use the function go there click right that's the power of MCP so automate every damn
1:23:551 hour, 23 minutes, 55 secondspossible in the world and throw all the humans out from the job. Screenshot. So let's run
1:24:021 hour, 24 minutes, 2 secondsallow some screenshot was taken. Not taken.
1:24:151 hour, 24 minutes, 15 secondsI need to know where it went. Let me try again.
1:24:241 hour, 24 minutes, 24 secondsOkay. something is blocking at my computer or maybe it's getting stored somewhere else.
1:24:321 hour, 24 minutes, 32 secondsCan you reload your files?
1:24:411 hour, 24 minutes, 41 secondsIt's not there. So that's why I'm checking.
1:24:451 hour, 24 minutes, 45 secondsUh maybe it go went on the desktop because only on Mac. Yes.
1:24:541 hour, 24 minutes, 54 secondsNo, I'll debug that. Not the time to debug with you guys. But yeah, it went somewhere.
1:25:021 hour, 25 minutes, 2 secondsShould have should have gone inside this. Okay, then what else do we have?
1:25:061 hour, 25 minutes, 6 secondsWe have I can add a note and other stuff. I just wanted to show you one more thing which is
1:25:131 hour, 25 minutes, 13 secondsfetch URL. Now let's go and fetch
1:25:221 hour, 25 minutes, 22 secondsmaximum characters you can define here and run tool. Now it's connecting internet going to uh school of AI and getting the result and done. These are
1:25:311 hour, 25 minutes, 31 secondsthe results that is there. So it's got the full HTML stuff right and of course like we will like to filter it out and give it
1:25:391 hour, 25 minutes, 39 secondsto LM. We will not like to send what do what do you know about school? is going to look at this website. It's going to say school of AI is a global site tag
1:25:471 hour, 25 minutes, 47 secondsGTA gtag.js Google Analytics blog. We don't want all of that. We wanted to come look at a main content and tell us what what is it right? This is literally
1:25:551 hour, 25 minutes, 55 secondsMCP. Now resources we're going to look at them later on. But in the resources we essentially provide um some images,
1:26:021 hour, 26 minutes, 2 secondssome text, some documentation, some PDF that are only read only, right? Why would you need that? For example, RBI gives us a uh MCB tool. I want to know
1:26:101 hour, 26 minutes, 10 secondswhat is the current repo rate. has done that I want to calculate something if I uh want to apply for a change on Aadhaar card on I like to go to Aadhaar website
1:26:181 hour, 26 minutes, 18 secondsand get the documentation of how should I do it or what function should I use right maybe uh Indian government
1:26:251 hour, 26 minutes, 25 secondslaunches a MCP Indian gov they will have millions of functions I will not like to just list all the tools moment I list
1:26:321 hour, 26 minutes, 32 secondsall the tools and send it to my LLM it has all of this context it is going to get confused so better would be that why don't I go to a resource and see okay I
1:26:401 hour, 26 minutes, 40 secondswant to change the GST number or I want to apply for the change of my uh address and that's a procedure. So going to tell me that okay use this function use that
1:26:471 hour, 26 minutes, 47 secondsfunction use that function and my life is simpler. That's what resources are and we are going to look at other things as time come. Any question on what we are seeing on the screen right now?
1:26:571 hour, 26 minutes, 57 secondsOkay. Deepak. No that's fine.
1:27:041 hour, 27 minutes, 4 secondsOkay. And then lower your hand. Uh Mohammed.
1:27:111 hour, 27 minutes, 11 secondsHey. Yeah. This this looks very interesting. Um so I had a couple of questions. So when you say the uh this is what the LLM will be using to call
1:27:201 hour, 27 minutes, 20 secondsthe various tools that we have in the system. So how uh I what I understand is the LLM is some kind of a model that
1:27:271 hour, 27 minutes, 27 secondsruns on like not in your local but you are interacting that from your local using an agent. So how is that
1:27:341 hour, 27 minutes, 34 secondsinteracting with your local disk? So is that giving instructions to some other agent that's running in your local to do that?
1:27:401 hour, 27 minutes, 40 secondsNo mpm is giving instruction to MCP. MCP is running that function and returning back. You saw that function already. So
1:27:481 hour, 27 minutes, 48 secondsif back here, it is going to call write
1:27:581 hour, 27 minutes, 58 secondsrun command, right? So it's running in the MCP server.
1:28:031 hour, 28 minutes, 3 secondsOkay. So the LLM is talking to this uh and say like execute go execute this. Um okay.
1:28:091 hour, 28 minutes, 9 secondsOkay. And the second question I have is like I see that you have written this in Python. So is that the only language that supports MCP or can I write a Java program and expose that in as an MCP?
1:28:201 hour, 28 minutes, 20 secondsNot Java. Java is dead. Uh Python or TypeScript. JavaScript which is not Java.
1:28:281 hour, 28 minutes, 28 secondsOkay. And and finally can you just show me the structure again like um uh the request structure that it um the LLM is
1:28:351 hour, 28 minutes, 35 secondsgoing to use to send the data. Uh the request Okay. So this is the standard request structure for any tool call that MCP.
1:28:471 hour, 28 minutes, 47 secondsYes. Go to receive from the LLM. Yes. Great. Thanks Rohan. Okay.
1:28:531 hour, 28 minutes, 53 secondsUm I my question basic uh so I'm a little confused over here. uh when we have tools those tools are uh listed in
1:29:031 hour, 29 minutes, 3 secondsthe context and the LLM knows about it and the first call lists the tool call itself which tool to call. So now you
1:29:121 hour, 29 minutes, 12 secondshave uh got you have an MCP server where all the tools are listed. Now how does
1:29:191 hour, 29 minutes, 19 secondsthe LLM know about it or it does not have to know about it?
1:29:231 hour, 29 minutes, 23 secondsIt needs to know about it but that's the next topic. Oh, it's the next topic today only.
1:29:281 hour, 29 minutes, 28 secondsDon't worry. I I will not leave you hanging. Okay.
1:29:321 hour, 29 minutes, 32 secondsOkay. Um uh so u maybe we'll I'll understand that also later.
1:29:381 hour, 29 minutes, 38 secondsSo u how did it know that this is the format in which the call has to be made?
1:29:451 hour, 29 minutes, 45 secondsThat is not the LLM's concern. I guess not LM's concern but the way we provide the list to LM it becomes very clear.
1:29:541 hour, 29 minutes, 54 secondsOkay. Uh final question uh I see there is some effort involved in listing those these tools over here. Uh what you have written are basic ad and all that stuff.
1:30:041 hour, 30 minutes, 4 secondsMaybe we have bigger things to do more complex things to do. We are still putting in the same effort with writing
1:30:111 hour, 30 minutes, 11 secondsthose tools. So where do we save the time and effort?
1:30:161 hour, 30 minutes, 16 secondsThe function is already written. I just wrote at MCP tool.
1:30:211 hour, 30 minutes, 21 secondsAll time and effort is same. If your legacy application has millions of functions on top of each function, just go ahead and write add MCP tool. That's
1:30:291 hour, 30 minutes, 29 secondsall. In fact, that also can be automated. You can write another script that looks at a function, right? Writes uh add MCP tool on top of it and then provides it to the to the MCP server.
1:30:381 hour, 30 minutes, 38 secondsThat can also be done.
1:30:401 hour, 30 minutes, 40 secondsOkay. So, the rest of the job is the tool discovery which you will explain later. Yes. Okay. Okay. Thank you.
1:30:481 hour, 30 minutes, 48 secondsOkay. Uh can you hear me? Yeah.
1:30:551 hour, 30 minutes, 55 secondsSo uh this MCP just now we just looked at it is stdio and when we look when we
1:31:031 hour, 31 minutes, 3 secondsrun that connect it is actually running um running that NCB server inside uh
1:31:121 hour, 31 minutes, 12 secondsinside that web app that is being spawned. uh if I understand correctly because there there were challenges that I was facing uh to connect uh initially
1:31:211 hour, 31 minutes, 21 secondsthat UV command that has been written there in the um so what I'm trying to understand is
1:31:291 hour, 31 minutes, 29 secondsthis web app is different and MCP server is different which is internally being invoked inside that web web app is that
1:31:371 hour, 31 minutes, 37 secondsthe case that's the case okay and so HTTP way of uh HTTP way of
1:31:451 hour, 31 minutes, 45 secondsuh HTTP protocol when we have to use with MCP that's a different server configuration correct are we going to look at that kind of a
1:31:531 hour, 31 minutes, 53 secondsnot today but yes today it not today but yes okay
1:32:001 hour, 32 minutesokay yeah hi Kishan here
1:32:061 hour, 32 minutes, 6 secondsuh in uh in the protocol uh so we saw different kind of responses right uh some response were just single index and
1:32:151 hour, 32 minutes, 15 secondssome text. Some responses like Fibonacci and uh multiple uh hold on indexes. No, no, every response is just text.
1:32:231 hour, 32 minutes, 23 secondsText.
1:32:251 hour, 32 minutes, 25 secondsThis is website. Okay. Every response is always just going to be text.
1:32:301 hour, 32 minutes, 30 secondsText again. Response is always text. The protocol defines that my response is always going to be text because LM accept text only text.
1:32:381 hour, 32 minutes, 38 secondsOkay, fair enough. And then it will tokenize uh whatever that is in the text. Correct. Okay. Okay. Proceed.
1:32:491 hour, 32 minutes, 49 secondsUm, hi Rohan. So the flow is something like this. The LLM connects to the MCP and MCP presents the catalog of all the functions it has.
1:33:011 hour, 33 minutes, 1 secondNo, the flow is going to be we launch a agentic framework. Agentic framework will make the connection to MCP and get
1:33:081 hour, 33 minutes, 8 secondsthe list of the tools. those list of tools will be sent to the LM along with the prompt.
1:33:151 hour, 33 minutes, 15 secondsOkay. Then it directs the MCP tool to do a function uh and then the results will be MCP you
1:33:231 hour, 33 minutes, 23 secondsknow function result will be sent to the LM again and it will utilize uh you know for the user context and presence right sort of yes correct. Okay. Thank you.
1:33:311 hour, 33 minutes, 31 secondsOkay.
1:33:321 hour, 33 minutes, 32 secondsUh no sorry actually I raised and started I think you have one question for me on the sandbox. So for the LMS to
1:33:411 hour, 33 minutes, 41 secondsprovide the sandbox is this a way Rohan where the MCP with the sandbox we need to provide that's correct.
1:33:491 hour, 33 minutes, 49 secondsOkay.
1:33:501 hour, 33 minutes, 50 secondsAnd uh we need to provide a list of commands and all we're keeping things very simple right now. Okay.
1:33:571 hour, 33 minutes, 57 secondsOkay. Sra uh Rohan like uh on the flow of the things right usually in an agent what we
1:34:061 hour, 34 minutes, 6 secondsdo uh is like we we write something in a free flow text right I want an answer of
1:34:131 hour, 34 minutes, 13 secondsadd to uh like you know sum of two numbers that's all we write and then can you explain like the moment tip for that
1:34:211 hour, 34 minutes, 21 secondshow the flow works to get the answer which how the MCP gets it's connected and we get the answer like I'm I'm not
1:34:301 hour, 34 minutes, 30 secondsable to do that connection I've not uh explained that that's the next topic that I'm going to cover after we all agree that we understand what MCP
1:34:371 hour, 34 minutes, 37 secondsis doing how LM NCP connection happens that's the next topic okay now answering your question how
1:34:451 hour, 34 minutes, 45 secondswill that happen because that will again help us in the next next topic that we cover our agentic framework is going to make the connection with the MCB the
1:34:531 hour, 34 minutes, 53 secondsfirst thing it's going to do is to call list tools moment we call list tools.
1:34:581 hour, 34 minutes, 58 secondsThe application is going to get the list of all the function data available in a particular format. That format is going to be appended or prepended depending on
1:35:071 hour, 35 minutes, 7 secondsreligion uh to the system prompt that we going to send to the LLM. Now, specifically for AD, for example, if I ask Claude, what
1:35:161 hour, 35 minutes, 16 secondsis 2 plus 2? It's going to say four. We have to force it to use add. We're going to say do not use always use a function call, right? Do not do any any
1:35:241 hour, 35 minutes, 24 secondsmathematical. So once that is a part of the function or a prompt claude is going to see or opus is going to see that okay I need to use this function this is how
1:35:311 hour, 35 minutes, 31 secondsI call it these are two numbers that the user ask me then uh chpd or opus is going to return back
1:35:401 hour, 35 minutes, 40 secondscall function in this particular format we're going to capture that particular format from JSON we're going to execute that mcp tool will be called result is
1:35:471 hour, 35 minutes, 47 secondsgoing to be uh we going to get the result as we saw here that result is going to be done taken and sent to the opus back op is going to see okay I was
1:35:561 hour, 35 minutes, 56 secondsasked to do this this is the user query this is how it will call this is the result then it's going to say uh you asked me to calculate 45 + 45 the answer
1:36:041 hour, 36 minutes, 4 secondsis 90 that's a flow but we're going to see that flow next ran just one followup like sometimes
1:36:111 hour, 36 minutes, 11 secondsit's not only one MCP that is there in our agent like we have multiple MCPS answering that is there that's where the skills will come in
1:36:201 hour, 36 minutes, 20 secondscome but not today's topic those are you are going in a direction of skills I have Gmail skills. When we say Gmail
1:36:291 hour, 36 minutes, 29 secondsskills, I have only made access to the Gmail MCP. I have PowerPoint skills.
1:36:341 hour, 36 minutes, 34 secondsThat's why skills are important. Skills is literally segregating thousands and thousands of functions or applications into different MCP servers and accessing only one MCP server in in the context.
1:36:451 hour, 36 minutes, 45 secondsSo, I can spawn a new agent with the skill for PowerPoint, do all the PowerPoint stuff, and then get rid of it. But we're going to cover that in the future session. But that's the skill.
1:36:561 hour, 36 minutes, 56 secondsGot it. Okay.
1:36:591 hour, 36 minutes, 59 secondsYeah. I was curious to know where the LLM integration is happening. I think maybe you'll show it next, right? Like LM integration is happening at 1 p.m.
1:37:081 hour, 37 minutes, 8 secondsOkay. Okay. Aash.
1:37:121 hour, 37 minutes, 12 secondsUh yeah Rohan. So two questions. Uh this LLM um the MCP that MCP.2 tool that is standard across all the uh MCPS right?
1:37:241 hour, 37 minutes, 24 secondsYes. So if we Okay. Okay. Okay. And uh and like these are not birectional. These
1:37:331 hour, 37 minutes, 33 secondsare just the functions which are one like take the input return the output and if you want a birectional like
1:37:401 hour, 37 minutes, 40 secondswe have streamable HTTP that we'll cover later. Okay sir. Okay that's it. Thank you.
1:37:481 hour, 37 minutes, 48 secondsYeah I'm done.
1:37:501 hour, 37 minutes, 50 secondsOkay. Uh Susan yes two questions uh for each function you have written some dock string right
1:37:581 hour, 37 minutes, 58 secondswhat happen if I remove all the dock string will it be same I mean will my MCP server understand what it is doing
1:38:061 hour, 38 minutes, 6 secondsno then from okay then from context for example if I remove this and you read this and you're reading the name of the function as review code then uh AI needs
1:38:151 hour, 38 minutes, 15 secondsto be smart enough to understand that so we make sure that we have double uh security here the function name is also done properly and then we have dock
1:38:231 hour, 38 minutes, 23 secondsstringing also but if doxing is not there a function here says that r c because you were lazy then problem
1:38:321 hour, 38 minutes, 32 secondsokay the second question is if you can go back to your uh canvas where you have list down uh four items
1:38:401 hour, 38 minutes, 40 secondsprobably ah wait over here so how this is going to fit in our particular model is that nothing but a every tool call
1:38:481 hour, 38 minutes, 48 secondsthis 1 2 3 4 is nothing but a tool function in uh the demo you have shown. Exactly. If I want to it.
1:38:561 hour, 38 minutes, 56 secondsYes, it's a tool. All right. Okay. Fine. Okay. Thank you.
1:39:051 hour, 39 minutes, 5 secondsHey. Uh yeah. Um I was curious on the way that you listed that the government has uh a lot of uh tool like functions
1:39:141 hour, 39 minutes, 14 secondslet's say right. So do you grab them or how do you contact with them or resource? You saw we had a resource thing also.
1:39:211 hour, 39 minutes, 21 secondsSo it it job of government to provide the list of resources. Resources would be GSC resource or income tax report
1:39:281 hour, 39 minutes, 28 secondsresource or ed rate report or corruption report. So there will they will list the MCP tools and we can just list them and
1:39:351 hour, 39 minutes, 35 secondsuse them. We we will be scared of calling all the tools.
1:39:401 hour, 39 minutes, 40 secondsRight. and and for specific context in those uh MCB tools I know we have covered this but sometimes there are like hundreds of function layers in
1:39:481 hour, 39 minutes, 48 secondsbetween so is grapping useful at all or it's just gone grapping is for local thing right your
1:39:551 hour, 39 minutes, 55 secondsLM can't grap LM can only output a text okay okay okay
1:40:041 hour, 40 minutes, 4 secondshi man u whatever you want to ask uh you have answered But still I would say like the my understanding just validate
1:40:121 hour, 40 minutes, 12 secondswhether it's right or not. Okay. So uh the system prompt it is there. The system prompt will call the list of the
1:40:201 hour, 40 minutes, 20 secondstools from the MCP. It will return the framework will call the list of uh tools and append to the system prompt.
1:40:291 hour, 40 minutes, 29 secondsOkay. It will append to the system prompt and then LLM will decide which tool what all the tools are required from these uh frameworks listed tools.
1:40:381 hour, 40 minutes, 38 secondsOkay. And that tools for this task this tool is required. For this task this tool is required. List of all the tools at a time it will be given and then lm
1:40:471 hour, 40 minutes, 47 secondsplus function call will happen the sequentially. Okay. Exactly.
1:40:511 hour, 40 minutes, 51 secondsAnd now the second question is that the in the uh MCP I keep on hearing the client server host. Okay. Can you please
1:40:591 hour, 40 minutes, 59 secondselaborate the so that the uh it would fit in my mind. Yeah. 1 p.m. 1 p.m. Okay.
1:41:081 hour, 41 minutes, 8 secondsThe other thing like the resources you were talking so what is the difference between the resources and tools?
1:41:131 hour, 41 minutes, 13 secondsResources is read only PDF, PNG, images, text tools are tools.
1:41:191 hour, 41 minutes, 19 secondsOh the only documentations documentations for how do we use it or some for example I give example of RBI reporate right? RBI or or ICIC interest
1:41:291 hour, 41 minutes, 29 secondsrate. So when we are calculating EMI using ICIC tool, what is the interest rate I should use? If I'm 65 year old and a woman and veteran of army. So the
1:41:381 hour, 41 minutes, 38 secondsrules will be written there. So I can read the resource. Oh my for me it's 5.5. So I can calculate that.
1:41:441 hour, 41 minutes, 44 secondsSo when when we say like the uh this blender MCP okay uh this um like the
1:41:511 hour, 41 minutes, 51 secondspostgress SQL uh MCP. So rather than calling the MCP can't we say that the key uh this is the blender server this is the uh
1:41:591 hour, 41 minutes, 59 secondsthat is what we say we say blend MCP server we say SQLite MCP server okay okay uh okay fine and uh this um
1:42:101 hour, 42 minutes, 10 secondsthe another question I have uh can we write the our custom function and expose to the MCP server and then we can integrate with the LM and see how it
1:42:191 hour, 42 minutes, 19 secondsworks is that that's what we are Aa that's what we are doing. Okay.
1:42:271 hour, 42 minutes, 27 secondsOkay. S thank you.
1:42:311 hour, 42 minutes, 31 secondsYeah. Uh like uh MCP basically like uh interaction for LLM uh LLM to call the tools right?
1:42:391 hour, 42 minutes, 39 secondsYeah.
1:42:411 hour, 42 minutes, 41 secondsYeah. Uh are there any tech or uh any other uh efficient way instead of MCP like uh right now? No.
1:42:511 hour, 42 minutes, 51 secondsJust just look at this page. I'm still scrolling and I I actually click marketing. Let me scroll.
1:43:011 hour, 43 minutes, 1 secondUh like there there are any upcoming things for replace MCP. No.
1:43:091 hour, 43 minutes, 9 secondsYeah. Thanks Samra.
1:43:131 hour, 43 minutes, 13 secondsHey I have a quick question about um the context from the company perspective. So
1:43:191 hour, 43 minutes, 19 secondslet's say I have a project okay and um obviously it has functions and stuff
1:43:261 hour, 43 minutes, 26 secondsthat it does right uh then I have a Jira server which tells like where the business puts in a Jira okay I want this
1:43:341 hour, 43 minutes, 34 secondsto be changed in this project right so Jira there is MCP so let's say I go into
1:43:401 hour, 43 minutes, 40 secondsanti-gravity or I go into VS code and I ask the agent that read my Zera server
1:43:471 hour, 43 minutes, 47 secondsand read my project which we are in the process of converting that into MCP uh
1:43:541 hour, 43 minutes, 54 secondsand then implement this whatever the J is asking implement this let's say so things if you can go to the code uh
1:44:031 hour, 44 minutes, 3 secondsplease uh so let's say that is my project if you can go to the screen please thank you so if I don't so
1:44:111 hour, 44 minutes, 11 secondsobviously because it has been written for a while I don't have line number 294 a lot of things a lot of functions will
1:44:181 hour, 44 minutes, 18 secondsnot have the details of what that exact uh function or that um service is doing the API is
1:44:261 hour, 44 minutes, 26 secondsdoing. So the first step is to ask LLM or something to read through all the code and create this.
1:44:351 hour, 44 minutes, 35 secondsYeah, you're asking this question for the second time I think and answer is yes. First thing would be to restructure the code at least write a dock string otherwise just send a whole code file if it is internal to you.
1:44:461 hour, 44 minutes, 46 secondsOkay. and then ask do I have to manually go into every function and write either mcpto tool or can I ask the agent to
1:44:551 hour, 44 minutes, 55 secondsjust make it a you will ask clot code to do it for you today yes okay okay cool thank you
1:45:031 hour, 45 minutes, 3 secondsyeah uh just wanted to check so all this interaction between the MCP and the LLM will actually happen via the harness
1:45:111 hour, 45 minutes, 11 secondswhether it's the agent or whether it's cloud code and it's it's the cloud code that will actually do the function call and return the result back to the LLM for further
1:45:191 hour, 45 minutes, 19 secondsexactly and I I want you to appreciate the authentication also. So here authentication was not required but let's say I was accessing Gmail the
1:45:271 hour, 45 minutes, 27 secondsauthentication will be required. So the first thing the MCP server handshake the hardness will have to do is on the authentication side. So authentication will done environment variable will be
1:45:351 hour, 45 minutes, 35 secondsset configuration will be set and then I can talk. Configuration will have how much time I have for timeout. For example, I'm reading a big file downloading GBs of data. So my timeout
1:45:431 hour, 45 minutes, 43 secondsneeds to change. So these are some things that we're going to go in future but yes the communication handshake between the MCP tool and the harness
1:45:511 hour, 45 minutes, 51 secondswhich is clot code or anti-gravity or cursor or codeex will happen first then the element will come into picture.
1:45:591 hour, 45 minutes, 59 secondsThanks. Okay.
1:46:011 hour, 46 minutes, 1 secondYeah. So uh Rahul I think my question is to whatever asked uh suppose I have a legacy application
1:46:121 hour, 46 minutes, 12 secondsthat if I convert those details to NCT uh I can reach in my local agent I'm
1:46:191 hour, 46 minutes, 19 secondswriting a local but if I wanted other people to write a on my NC whatever to
1:46:301 hour, 46 minutes, 30 secondsso I need to register those APIs from my server or how they will read my code at all how they call my
1:46:391 hour, 46 minutes, 39 secondsuh on your website you have to just host your MCP um list essentially that's all
1:46:461 hour, 46 minutes, 46 secondsit's just a it's just a Python file okay Pushka
1:46:561 hour, 46 minutes, 56 secondshi Rohan uh so the MCP host that that we have created right now Right. Uh it's in the Python. So is it the only way that we can uh write MCP server as of now?
1:47:061 hour, 47 minutes, 6 secondsEither Python or JavaScript.
1:47:081 hour, 47 minutes, 8 secondsOkay. Okay. And uh the functions that we have written, right? So it can be any native uh API that that can be exposed in general, right?
1:47:171 hour, 47 minutes, 17 secondsThat's correct.
1:47:191 hour, 47 minutes, 19 secondsOkay. And the MCT inspector that we have we are seeing uh that is just a place to check how each of the function would uh
1:47:271 hour, 47 minutes, 27 secondswork and all. Is it is sort of integration uh unit testing? That's correct.
1:47:321 hour, 47 minutes, 32 secondsOkay. And yeah, is it possible that one function can call another? That's correct.
1:47:381 hour, 47 minutes, 38 secondsIt need not be independent, right? So one can call another. Correct. Okay. Okay. That's all. Thank you.
1:47:451 hour, 47 minutes, 45 secondsOkay. Pravin. Yeah. So without sandbox there's no MCP. Without what?
1:47:531 hour, 47 minutes, 53 secondsWithout sandbox.
1:47:551 hour, 47 minutes, 55 secondsNo. Sandbox is required if you want to run a code.
1:47:591 hour, 47 minutes, 59 secondsOh okay. Otherwise it doesn't require and it is not mandatory. Not mandated at all. No. Thank you. Okay.
1:48:101 hour, 48 minutes, 10 secondsYeah. Uh so after integrating with the LLM so the LM will take the decision based on the do stream present in the tool or the function.
1:48:191 hour, 48 minutes, 19 secondsCorrect.
1:48:201 hour, 48 minutes, 20 secondsSo do we require like bigger models to take the decision? I mean like bigger models means more tokens and uh cost
1:48:271 hour, 48 minutes, 27 secondswill increase like smaller models will work right if it is smaller models will work. Yeah 2026 smaller models will work.
1:48:351 hour, 48 minutes, 35 secondsSo then you can use the smaller models to make the decision so that you can say the tokens. Correct.
1:48:421 hour, 48 minutes, 42 secondsWhat you need to remember is if in in your flow you need 10 20 MCP tool calls smaller models will struggle. Smaller
1:48:491 hour, 48 minutes, 49 secondsmodels are really good for four five uh context right.
1:48:551 hour, 48 minutes, 55 secondsSo small models means like it is 100 million to 100 million parameters or 7 billion considered as a small models small today like for coding this kind of
1:49:031 hour, 49 minutes, 3 secondswork I think 20 to 30 billion parameters are safe 35 billion like where where your gamma 4 and quen is there.
1:49:121 hour, 49 minutes, 12 secondsMhm. Okay. Those are really good. Yeah. Thank you. Okay.
1:49:171 hour, 49 minutes, 17 secondsYeah. I think you've explained how how work with but before that you also
1:49:261 hour, 49 minutes, 26 secondsinclude right that some before NC few few companies tried to have their own uh
1:49:341 hour, 49 minutes, 34 secondslogin plugins for various different different services. Yes.
1:49:391 hour, 49 minutes, 39 secondsSo how did that happen? I mean they were man they were manually writing all of this for every single API.
1:49:461 hour, 49 minutes, 46 secondsOkay. manually writing the input and the output I mean making the input output same. Yes.
1:49:521 hour, 49 minutes, 52 secondsOkay. And then then the similar way of telling the model that these are the correct okay.
1:50:001 hour, 50 minutesYeah. The way uh you're showing it right now the MCP server is there where we can see the list of tones and we interact
1:50:071 hour, 50 minutes, 7 secondswith that uh function directly. Now I'm just trying to figure out like where is the LM here? I mean LM is at 105 p.m.
1:50:211 hour, 50 minutes, 21 secondsYeah. Okay. Sata.
1:50:241 hour, 50 minutes, 24 secondsUh Rohan. Uh hi. So here we have created a host and we are reading it through MCP inspector. So can I see an already existing um um from the web like zoom?
1:50:351 hour, 50 minutes, 35 secondsUm can we take an example like zoom and uh can I see some re what can we read from zoom zoom mcp? What?
1:50:441 hour, 50 minutes, 44 secondsYeah, I I shared a link on the chat.
1:50:461 hour, 50 minutes, 46 secondsClick that link, search for Zoom and click there and inside you will find all the MCP tools.
1:50:511 hour, 50 minutes, 51 secondsUh okay, fine. Uh understood. Uh awesome MCP servers. So how to integrate that into this MC inspector? I mean um just download the MCP file.
1:51:011 hour, 51 minutes, 1 secondUh okay. Okay. I I'll try.
1:51:081 hour, 51 minutes, 8 secondsHey Roan, let's see if we have too many MCB tools, right? skills also the context answer skills we'll cover that in future sessions but that's what skills are if
1:51:171 hour, 51 minutes, 17 secondsyou have heard about them okay okay okay uh yeah uh Roan uh can you get more
1:51:261 hour, 51 minutes, 26 secondsinformed transport type and which one we should use if you're deploying MCP server in production you don't need uh SSE uh we do not have
1:51:341 hour, 51 minutes, 34 secondsenough discussions even done on MC on SSE so it will come in future but that will be for real-time communication you want to have a So for example, if you're
1:51:421 hour, 51 minutes, 42 secondsdoing stock trading, you definitely need SSE. You continuously options trading basically you continuously need data. Okay.
1:51:491 hour, 51 minutes, 49 secondsOr streaming something then we'll need SSE. So this doesn't work on top of HTTPS. Yeah, something like that.
1:51:561 hour, 51 minutes, 56 secondsSomething like that. Yes. Okay. Uh Karthik Karthik sorry.
1:52:041 hour, 52 minutes, 4 secondsYeah. Hi Ro. uh so when we talked about this right a hardness wherein uh uh that will responsible uh harness and uh will
1:52:121 hour, 52 minutes, 12 secondsbe responsible to connect with MCP and then uh authentication will be taken care of so I want to know what the harness in simple terms like cloud code and these are things at 1 p.m.
1:52:221 hour, 52 minutes, 22 secondsOkay. Isn't that the same thing we did in last class like that while loop wherein we are managing everything? Exactly what we did last time. Yes.
1:52:311 hour, 52 minutes, 31 secondsOkay.
1:52:311 hour, 52 minutes, 31 secondsAll right. I need a very very important
1:52:451 hour, 52 minutes, 45 secondsbreak. I'll be back in 2 minutes.
1:55:101 hour, 55 minutes, 10 secondsAll right. Now, let's move to the next part.
1:55:221 hour, 55 minutes, 22 secondsOkay, before we move in, uh, let me make sure I've covered some important bits. So, there are two ways of calling it.
1:55:301 hour, 55 minutes, 30 secondsOne is Python example. Don't we, we can't hear you.
1:55:351 hour, 55 minutes, 35 secondsI was not speaking. I was just like mimicking.
1:55:381 hour, 55 minutes, 38 secondsSo, uh, we're going to basically see two things.
1:55:431 hour, 55 minutes, 43 secondsThe way we call MCB server is Python example MCB server.py. Uh when we write our hardness or when we write our u
1:55:501 hour, 55 minutes, 50 secondsprogram or orchestration there we are going to call this Python uh example MCB server automatically using Python. So Python can call another another file.
1:56:001 hour, 56 minutesBut when we're testing a server we're going to be writing MCB example MCB server or whatever your file server file is and we can get this front end where
1:56:071 hour, 56 minutes, 7 secondswe can play around with it. Now first time you write it my request is that you use your front end to see it is working or not. Sometimes MCP servers fail and
1:56:171 hour, 56 minutes, 17 secondswe have no idea why it has failed. But if this file if the dev server is not opening up you know the MCP server has a problem right and then you can
1:56:241 hour, 56 minutes, 24 secondsimmediately fix it and clot code will take a bit of time to uh understand this because clot code is not teaching right clot code will think that I've done my
1:56:331 hour, 56 minutes, 33 secondswork I am always a genius and I will always not make any error and you might actually get stuck there. So first time you write MCB server, make sure that you
1:56:401 hour, 56 minutes, 40 secondsgo uh and write this command MCP dev or you can ask clot code to do it because you're so lazy that it will open a dev server. You can test it there. You can
1:56:481 hour, 56 minutes, 48 secondstest some of the outputs and then uh uh revert back. Now this is also important for you to see what is happening. Now
1:56:551 hour, 56 minutes, 55 secondswhen we are looking at a rag, right, I told you rag for us is going to be literally MCB tool. uh query comes in,
1:57:021 hour, 57 minutes, 2 secondsit calls another embedding tool to find the best embeddings and gets us the snippets and you can get the result.
1:57:081 hour, 57 minutes, 8 secondsNow, if you depend on the loop to solve the whole rag problem, you're going to get stuck there again. You need to be on the dev server, send a query directly
1:57:161 hour, 57 minutes, 16 secondsfrom here and see what the tool is returning. So, you know that okay, your tools lm is not hallucinating, the data is not good. So, it is required for you
1:57:241 hour, 57 minutes, 24 secondsto debug properly. There is a bit of coding still required. uh of course cloud can take care of all of that but it's to save time and save tokens and
1:57:321 hour, 57 minutes, 32 secondssave money and uh maybe to do things faster compared to what clot can do right so some uh things can still be faster than just depending on clot now
1:57:411 hour, 57 minutes, 41 secondswe also discussed that this is the way we uh send the request to MCB tool MCB server and this is the way we get a response response is always text because
1:57:481 hour, 57 minutes, 48 secondsLLM needs text right and uh this may change in future I think this should change in future because sometimes um we
1:57:581 hour, 57 minutes, 58 secondsjust don't want text. We want to know whether the text has uh JSON, whether a text has code, whether text has numbers,
1:58:071 hour, 58 minutes, 7 secondswhether text has a file, whether text is a URI or HTTP, some additional metadata would really help. And I'm seeing some progress happening in that direction.
1:58:141 hour, 58 minutes, 14 secondsBut once you start working with MCP, then you realize a pain that there is a little bit of more context that could have helped. But I'm keeping the context limited to today's session. So it's
1:58:221 hour, 58 minutes, 22 secondseasier to absorb also. Okay. Now we also saw that we have tools, we have resources, we have prompts, we have pings, we have sampling, we have roots,
1:58:301 hour, 58 minutes, 30 secondsa lot of other things are there. Root is where my sandbox is there. So these things are going to help us as we go further into MCP. But today we are
1:58:371 hour, 58 minutes, 37 secondskeeping things very simple. We predominantly discuss tools which is list of all the functions that I can run and uh moment we get the list I get all
1:58:461 hour, 58 minutes, 46 secondsthe function that are listed there. The way we get the list is by calling this function called call tool. We're going to see that in the code. That's the thing that gets appended into the system prompt.
1:58:551 hour, 58 minutes, 55 secondsAnd we get a list of tools like this. So where does your dock string go? It goes in the description. Input schema is fixed. Input schema is already extracted
1:59:041 hour, 59 minutes, 4 secondsby looking at the MCP uh the the tool that is there. Right? And the result is always text. So we don't have to worry about it. So this is how the input
1:59:111 hour, 59 minutes, 11 secondsschema looks like. This is what is sent to the LLM, right? Name of the tool, description of tool, the input schema. A
1:59:181 hour, 59 minutes, 18 secondsis a title A type of integer. B is a title B type of integer. and required are a and b. We can't miss any of them.
1:59:251 hour, 59 minutes, 25 secondsThen title is add arguments and type of object. So this is what is sent to the lm. The lm is going to look at this kind
1:59:321 hour, 59 minutes, 32 secondsof list. Okay. Now let's talk about mcp server and client. Again we are not
1:59:391 hour, 59 minutes, 39 secondslooking at jumping directly onto the uh detailed uh lm calls but this will still help us. Uh we have a code here and code here. When you click on this, this
1:59:481 hour, 59 minutes, 48 secondsmagically opens some uh page where you can download the code also. So don't worry on that. You have the code already. So let's look at our MCP server
1:59:571 hour, 59 minutes, 57 secondsfirst because very similar to what we wrote earlier. So here I've written only one function. Okay, reverse string. I can copy paste all of them. But we're
2:00:062 hours, 6 secondskeeping things very simple. This is how structure of MCP server looks like. You can see there's literally nothing there.
2:00:112 hours, 11 secondsI'm just saying from MCP. Fast MCP import fast MCP. MCP equal to fast MCP string reverser MCP. pool and inside
2:00:182 hours, 18 secondsthat we have a function some doc string uh these things help uh understand uh I want a string I'm going to be written
2:00:262 hours, 26 secondsrunning a string that's all right and then these are print statements that that we're going to get and then we have a client now how do we actually connect
2:00:352 hours, 35 secondsto MCP right now when we did mcp dev example mcp_server py this was being done by the mcpdev uh tool for us but
2:00:442 hours, 44 secondsthis is how we are going to be uh connecting to any mcp server. Now we need to import client session and stdio
2:00:522 hours, 52 secondsserver parameters. Now stdio server parameter is going to be python command and the argument which is going to be
2:00:592 hours, 59 secondsmcb server right mcb server. This is required to understand how do we connect to particular mcb server. Now here we
2:01:062 hours, 1 minute, 6 secondsare doing a connection and when we do ssc we're going to see slight things slight change a slight thing that actually differ. we do a sync connection
2:01:142 hours, 1 minute, 14 secondsbecause we don't know when the functions are going to be returning the uh tool uh response uh with sddio with is basically
2:01:212 hours, 1 minute, 21 secondsa context in python uh moment I say with I am in context of something so with sddio as read and write I have both the
2:01:292 hours, 1 minute, 29 secondsrights a sync client session client session is something that we're again importing client session has a read and write as session so some things like two
2:01:372 hours, 1 minute, 37 secondsthree things that your uh cloud code and others will be able to very easily you do not have to worry about it. Now
2:01:462 hours, 1 minute, 46 secondsthis is the line where we are initializing a session. Now when we will have let's say 10 15 different MCP uh servers you're going to be awaiting session.initialize for each one of them.
2:01:572 hours, 1 minute, 57 secondsSo in I think two three sessions from now I'm going to be introducing multiMCP client where we'll have multiple MCP servers and we'll see how the code needs
2:02:052 hours, 2 minutes, 5 secondsto be written for all of that. But you are literally one prompt away from understanding that if you want to understand that today from clot code. So
2:02:122 hours, 2 minutes, 12 secondsonce the connection is done uh connect to MCP server is for the user you and me to see okay we are connected now nothing is wrong. If you do not get this line
2:02:202 hours, 2 minutes, 20 secondsprinted that means you are stuck at the MCP server itself. Again open the dev and see what is wrong. Maybe uh you return some uh function that can't be
2:02:282 hours, 2 minutes, 28 secondscalculated or some error is there in the code. Then I'm going to be prompted uh enter text to reverse and uh I know there's only one function to be called.
2:02:402 hours, 2 minutes, 40 secondsSo I'm going to be session doing a session call tool reverse string is the name argument is going to be text and text and result is going to be printed
2:02:472 hours, 2 minutes, 47 secondshere. So, let's clear my screen and let's run Python MCP
2:02:562 hours, 2 minutes, 56 secondsclient and I'm going to say run and it's going to tell me uh processing request of type
2:03:052 hours, 3 minutes, 5 secondscall tool request processing request and reverse text is now
2:03:112 hours, 3 minutes, 11 secondswhat all happened here now you you see that I'm not running mcps server.py py anymore, right? I did not do this python
2:03:202 hours, 3 minutes, 20 secondsfirst run mcp server. py. If I do that, I can do it.
2:03:262 hours, 3 minutes, 26 secondsBut I did not do it. I directly went inside my client and ah did that again. Sorry.
2:03:462 hours, 3 minutes, 46 secondsHey, what happened to this guy?
2:03:552 hours, 3 minutes, 55 secondsYou need to live with it. I don't know what happened. Uh, Python MCB client. I did not need to kickstart the server.
2:04:032 hours, 4 minutes, 3 secondsAnd here I can write for example India and it's going to reverse this thing and give us. So what all happened here? Now this is very short client file. We call
2:04:112 hours, 4 minutes, 11 secondsour initial prayers. Once that is done, we initialize the parameters for the server. And you can see that this is
2:04:192 hours, 4 minutes, 19 secondscalled server parameters. Server parameters went inside stdio client and stdio client uh inside stdio client I
2:04:272 hours, 4 minutes, 27 secondsinitialize the server. So these three lines initialize the server for us. So I do not have to initialize the server.
2:04:332 hours, 4 minutes, 33 secondsOkay. Now this is only possible for stdio where the requirement is I talk to the MCP server uh do one function call and just close the connection with that.
2:04:422 hours, 4 minutes, 42 secondsRight. and the connection is as long as my uh loop was running or I was doing something with that moment I exit this particular function everything's closed
2:04:492 hours, 4 minutes, 49 secondsyour SSE or uh the streaming server is going to be for a longer conversation that we that we're going to look at later on so we are still not with LLM
2:04:582 hours, 4 minutes, 58 secondsbut this is how we are going to be harnessing inside LM inside the LM what would have happened this would have been done connected to MCP server would be
2:05:052 hours, 5 minutes, 5 secondsdone then I'm going to not directly do this in between here I'm going to be calling the list of all the rules that are Then I'm going to take the system
2:05:142 hours, 5 minutes, 14 secondsprompt. I'm going to append the list of tools to the system prompt. Then I'm going to send it to my LM along with the query that the user has. So you are a uh
2:05:222 hours, 5 minutes, 22 secondsMcKenzie expert who can write a good presentation on Indian economy and blah blah blah. These are the tools that are available. Then the user query comes in that what do you think is going to be
2:05:292 hours, 5 minutes, 29 secondseconomy of India in 2047. Here are a tool right and uh it looks at okay this is a user query. These are tools I have.
2:05:372 hours, 5 minutes, 37 secondsIt's going to think internally. I can call that tool.
2:05:402 hours, 5 minutes, 40 secondsuh look at the internet download all the data and then make a prediction. So then the whole sequencing will start but this is literally the bare MCP client and
2:05:472 hours, 5 minutes, 47 secondsserver. Okay. Any question just from the client and the server we have still not touched the LLM that is do not ask me questions. LM is going to be at depending on your questions. Uh 115.
2:05:592 hours, 5 minutes, 59 secondsOkay.
2:06:012 hours, 6 minutes, 1 secondUm so why did you start the server from the client? Is that how it usually works?
2:06:072 hours, 6 minutes, 7 secondsThat is how it works for the S3O.
2:06:112 hours, 6 minutes, 11 secondsOh okay. So it always starts a new server, executes the request, close it, brings it. Yes.
2:06:192 hours, 6 minutes, 19 secondsSo the server is never running continuously.
2:06:222 hours, 6 minutes, 22 secondsA running server continuously is called SSE server which we have not looked at today.
2:06:272 hours, 6 minutes, 27 secondsOkay. Sorry, you've been saying that but I didn't understand.
2:06:302 hours, 6 minutes, 30 secondsNo problem. A yeah. Uh so why do we have a client architecture?
2:06:392 hours, 6 minutes, 39 secondsRepeat that again.
2:06:412 hours, 6 minutes, 41 secondsWhy do we need to have a client server architecture for why do we need to have a client server architecture? What what other
2:06:482 hours, 6 minutes, 48 secondsarchitecture can work? No, I I don't know. I mean this seems like there's a connection that is needed but for example the code that you were
2:06:562 hours, 6 minutes, 56 secondstelling showing us last time that was a simplistic code and we were uh doing that already. So those were also simple
2:07:042 hours, 7 minutes, 4 secondsand they did not need a kind of a client server.
2:07:102 hours, 7 minutes, 10 secondsI don't know how to get rid of this is irritating me. Those do not need client server. No, so we talking about MCP. How does MCP work? You're asking why do we
2:07:182 hours, 7 minutes, 18 secondsneed client server? How do I answer that question? This is how MCP works.
2:07:242 hours, 7 minutes, 24 secondsIf it is your code, if it is your function, you don't need this. You can just read the whole you can just take the whole API and dump it into your harness. But now you need to work with
2:07:322 hours, 7 minutes, 32 secondsuh let's say Blender, PowerPoint, uh window automation tools and other stuff.
2:07:362 hours, 7 minutes, 36 secondsIn that case, you can't take the code and put it inside, right? So, in that case, handshake is required. When you're going to, for example, read a Gmail, authentication is required. You can't
2:07:442 hours, 7 minutes, 44 secondsput all that code inside your code. In the last session, we wrote all the code inside our code.
2:07:522 hours, 7 minutes, 52 secondsOkay, Ganesh.
2:07:552 hours, 7 minutes, 55 secondsIn the actual scenario, you don't require the code at line number 19 to 22, right?
2:08:022 hours, 8 minutes, 2 secondsin the MCP client line number 19 to 22 you don't require that right in the actual scenario no we need that but that will be LM
2:08:102 hours, 8 minutes, 10 secondsdriven ah yes correct you don't need to put it in the client do we need to put it that in the client we need to put that in the client yes
2:08:172 hours, 8 minutes, 17 secondsyou're going to see that this this thing these two things will come from lm rest we need
2:08:262 hours, 8 minutes, 26 secondswe need to call the tool lm can't call the tool lm will tell us which tool to All okay.
2:08:332 hours, 8 minutes, 33 secondsOkay. Pit.
2:08:352 hours, 8 minutes, 35 secondsSo um in line 12 to 14 here in the client where do you mention which server to initialize server parameters?
2:08:472 hours, 8 minutes, 47 secondsOkay. Argument np.
2:08:492 hours, 8 minutes, 49 secondsOkay. Avin uh this is a handshake. Uh right?
2:08:552 hours, 8 minutes, 55 secondsThis is a handshake. Yes. These three based on the usage most of the things that like interact with like Azure or uh
2:09:052 hours, 9 minutes, 5 secondspost test so they all use this handshake right like basically the tokens and authentication will be stored in the
2:09:142 hours, 9 minutes, 14 secondslike CLI sessions correct whereas yeah okay thank you okay moment
2:09:232 hours, 9 minutes, 23 secondsso this particular MCP client program that we have written So uh I'm just like confused like why do we need that does the uh LLM or like um let me explain uh
2:09:322 hours, 9 minutes, 32 secondsask you that in a different scenario. So if you're using VS code or any other chat uh you have a agent chat here in
2:09:392 hours, 9 minutes, 39 secondsyour um anti-gravity as well. So I know we can also configure MCP server for this chatbot to use it. So this client
2:09:462 hours, 9 minutes, 46 secondsprogram is embedded in the chatbot client that it automatically knows how to connect to this MCP. That's correct.
2:09:522 hours, 9 minutes, 52 secondsOkay. So we are creating a kind of a chatbot like parallel correct to that key. Okay. Got it. So what you're seeing here is a agent.
2:10:002 hours, 10 minutesWe are making our own agent slowly. Okay.
2:10:042 hours, 10 minutes, 4 secondsBy the end of the course you should be able to write the whole uh anti-gravity yourself. Got it.
2:10:102 hours, 10 minutes, 10 secondsOkay. So what's uh Rohan? Hi. So here um we have created
2:10:172 hours, 10 minutes, 17 secondsa client to have a um session to create a session and to and to connect to the server and list all the methods and reverse the number. I understand that.
2:10:262 hours, 10 minutes, 26 secondsSo uh and there you have also run the command to connect to the server directly but you said we have to connect from the client.
2:10:332 hours, 10 minutes, 33 secondsUh they a bit confused. Uh Rahan, this is the client. What is the question?
2:10:382 hours, 10 minutes, 38 secondsUh correct. So uh here we Okay. Um we can't connect to the server directly. We have to connect from the client to the server and we have to get the context.
2:10:472 hours, 10 minutes, 47 secondsUh means they're a bit confused.
2:10:512 hours, 10 minutes, 51 secondsWe have we should not be able to connect to the server directly. We should connect from the client.
2:10:572 hours, 10 minutes, 57 secondsSomeone needs to start the server. We started the server from the client.
2:11:022 hours, 11 minutes, 2 secondsThese three lines highlighted are the uh lines required to start the server to connect to the server. Yeah. Fine
2:11:092 hours, 11 minutes, 9 secondssir. If you don't do this then you need to figure out a way in which you can pass the context of the server to the client somehow. So you're going to write more code.
2:11:182 hours, 11 minutes, 18 secondsUh-huh. Okay. Yeah. Okay. Sep.
2:11:222 hours, 11 minutes, 22 secondsYeah. Uh so Rahan we are talking about here server and client right now. Uh here the example that you are showing both the files basically are sitting
2:11:302 hours, 11 minutes, 30 secondsinto the same code or workspace and maybe that is the reason you were able to pass directly this py server. py file
2:11:382 hours, 11 minutes, 38 secondsas argument that need to be downloaded for every single application you want to connect to. So if you are connecting to a python let's say blender you need to have a blender server py. If you're connecting
2:11:462 hours, 11 minutes, 46 secondsto zoom you need to have a zoom uh server py it can also be hosted on zoom server. So you can really realtime download and link.
2:11:552 hours, 11 minutes, 55 secondsOkay. So just by passing this mcp uh server pi and if I create this client anywhere and initiate this client it
2:12:022 hours, 12 minutes, 2 secondswill be able to connect to those mcp servers.
2:12:042 hours, 12 minutes, 4 secondsExactly. because I don't see any port or because normal programming right what we do wherever like we want to connect to servers like we give the details of like
2:12:122 hours, 12 minutes, 12 secondsconnection strings and ports and everything I don't see that is here that is where SSA will come okay
2:12:212 hours, 12 minutes, 21 secondsokay okay so yeah so when we connect let's say GitHub MCP server into anti-gravity or cursor
2:12:302 hours, 12 minutes, 30 secondsuh we essentially initialize this MCP client yes I'm no we initialize the MCP server in the client.
2:12:392 hours, 12 minutes, 39 secondsOkay.
2:12:402 hours, 12 minutes, 40 secondsYou're uh when moment you said I'm in anti-gravity or cursor you are in the client already.
2:12:472 hours, 12 minutes, 47 secondsOkay. And and uh when we connect it essentially runs these three lines. I mean yes par. Thank you.
2:12:552 hours, 12 minutes, 55 secondsOkay. S uh I keep hearing the word harness. So what is an harness in a very layman term
2:13:042 hours, 13 minutes, 4 secondslike in this context this code that connects the connection is harness like harness is that thread that connects everything. So this is the
2:13:122 hours, 13 minutes, 12 secondsthread between our client and the server. Literally these three lines are the harness.
2:13:212 hours, 13 minutes, 21 secondsOkay. Okay. So whatever the connection between the client and server is the harness.
2:13:272 hours, 13 minutes, 27 secondsYes. the code that is required to make connections between different things.
2:13:302 hours, 13 minutes, 30 secondsThis and the LLM and the user is the whole harness thing. So whole this whole file I'll call as a harness it's it's just the synonym. Yeah.
2:13:412 hours, 13 minutes, 41 secondsBasically the chain of events that is going to happen uh yes like in a structured way is an harness.
2:13:482 hours, 13 minutes, 48 secondsCorrect. The thing that controls that chain of event which is the code is the harness.
2:13:572 hours, 13 minutes, 57 secondsUm so the client is what is going to convert the LLM call into a format that is required by the server.
2:14:132 hours, 14 minutes, 13 secondsNo LM will give you the uh exact commands or or exact text that makes it easy for the client to call the MCP tool.
2:14:242 hours, 14 minutes, 24 secondsIt gives the parameters and uh the client has to still create the exact JSON. No. And then no that that is exact that is exactly
2:14:322 hours, 14 minutes, 32 secondsthe point because we have made this protocol a language or a communication structure. LLM is always going to give us the structure of how we call a
2:14:412 hours, 14 minutes, 41 secondsparticular function. We're just going to copy paste and dump into a function to call it.
2:14:482 hours, 14 minutes, 48 secondsuh we I do not have to parse the fun the the lm output further. I just have to figure out oh lm call uh is lm calling a
2:14:562 hours, 14 minutes, 56 secondsparticular MCP tool. This is what it wants to do. I'll just dump it. So I do not have to do postprocessing on top of it. That's exact point of this MCP server.
2:15:042 hours, 15 minutes, 4 secondsNo will will the client have to do it?
2:15:072 hours, 15 minutes, 7 secondsNo, you're saying the LLM's output based on the MCP um servers the tools details or uh
2:15:162 hours, 15 minutes, 16 secondsattributes it's going to create a JSON which fits the bill. Correct. Right. That's correct.
2:15:232 hours, 15 minutes, 23 secondsOkay. So, uh uh can the same client cater to multiple servers like I need to
2:15:302 hours, 15 minutes, 30 secondsmake a database call. It could be DB2, it could be Oracle, it could be something else. And they're all served
2:15:372 hours, 15 minutes, 37 secondsby multiple MCT servers from those organ enterprises. So can the same client um
2:15:442 hours, 15 minutes, 44 secondswork with all those servers or is it one to one?
2:15:482 hours, 15 minutes, 48 secondsSame client can work with all as I said in the next few sessions we're going to write a multiMCP server file client which can connect to multiple MCP servers.
2:15:572 hours, 15 minutes, 57 secondsOkay.
2:15:592 hours, 15 minutes, 59 secondsOkay. Uh pushka uh Rohan can you explain any uh uh any scenario wherein uh we can have multiple clients connecting to the same server?
2:16:112 hours, 16 minutes, 11 secondsIs it like uh yes the same?
2:16:142 hours, 16 minutes, 14 secondsFor example, if you want to do this part, how you tell me how many things you need to connect to?
2:16:202 hours, 16 minutes, 20 secondsIt needs to connect uh to the API uh com uh the MCP API first. No, I think it
2:16:282 hours, 16 minutes, 28 secondsneed to connect to the Zoom API alone, right? And retrieve the information.
2:16:362 hours, 16 minutes, 36 secondsThis is one call. Sending a request to the Zoom one.
2:16:402 hours, 16 minutes, 40 secondsOkay. So, schedule a Zoom meeting with my team. Where's the team?
2:16:472 hours, 16 minutes, 47 secondsUh, which means to teams.
2:16:512 hours, 16 minutes, 51 secondsYeah. So, probably some tool where a team might be there, right? right?
2:16:572 hours, 16 minutes, 57 secondsMicrosoft Teams or something. Yeah, maybe maybe Google uh Gmail, maybe a chat. So, I need to connect to that.
2:17:032 hours, 17 minutes, 3 secondsThen I need to make a Zoom request. Now, after that, I need to put that on the calendar. So, I need a Google calendar. Mhm.
2:17:102 hours, 17 minutes, 10 secondsSo, I need three four here or just change this. Okay. Schedule a meeting with my team. Uh and uh drop down email.
2:17:172 hours, 17 minutes, 17 secondsSo, I say this, I need a Google calendar, Zoom, and email it.
2:17:252 hours, 17 minutes, 25 secondsOh. Um I still I'm not uh understanding the scenario wherein a single cl uh
2:17:322 hours, 17 minutes, 32 secondssorry multiple clients can be connecting to the same uh server multiple client same server. Okay you asking multiple client same server. So in that case you are YouTube and
2:17:412 hours, 17 minutes, 41 secondsmultiple people wants to connect to you uh which means like a different request but you all having the same sort of requirements correct or same infrastructure. Okay, got it.
2:17:512 hours, 17 minutes, 51 secondsThank you.
2:17:532 hours, 17 minutes, 53 secondsUh Ashanand uh yeah sorry again asking uh so uh okay
2:18:012 hours, 18 minutes, 1 seconduse case session uh this question is from use case. So I have an app okay we have built an app and uh I'll create an
2:18:092 hours, 18 minutes, 9 secondsAPIs and expose it uh token based and to use that APIs I need to create a MCP server and host it in the marketplace.
2:18:192 hours, 18 minutes, 19 secondsCorrect? If you are for others who use it. Yes.
2:18:222 hours, 18 minutes, 22 secondsIf it is only for you then not required really.
2:18:252 hours, 18 minutes, 25 secondsOkay. Uh and that at the rate MCP. Those will be there in the MCP servers. Correct. Uh okay boss. Okay. Okay.
2:18:352 hours, 18 minutes, 35 secondsOkay. Now because uh some people may still have question on that. Let's go to that awesome thing. Uh we done a Ashin.
2:18:472 hours, 18 minutes, 47 secondsUm yeah Ron. So it's just for better understanding of where this client server sits. Suppose I have an application.
2:18:552 hours, 18 minutes, 55 secondsYeah, I think this will answer your question also. So here we're looking at a blender MCP server, right? Somebody somebody made it. This is not for official blender also. So Aja said
2:19:022 hours, 19 minutes, 2 secondsSiddhhat Auja probably, right? This is required. So if I go in source blender MCP, I will have the server telemetry and telemetry. I go in server.py and I
2:19:112 hours, 19 minutes, 11 secondsdo just do Ctrl F uh MCP dot tool. You see that? So, get scene
2:19:192 hours, 19 minutes, 19 secondsinfo, get object info, uh, get viewpoint screenshot, execute Blender code. This file is all I
2:19:272 hours, 19 minutes, 27 secondsneed. So, I'm going to download this file. And in my code, I'm going to say python uh, source/blender_mcp/server.py.
2:19:412 hours, 19 minutes, 41 secondsAnd now I can control Blender on my computer. Now I ask you the question.
2:19:462 hours, 19 minutes, 46 secondsUh yeah. So uh if I have an application like Flipkart and we have the chat
2:19:532 hours, 19 minutes, 53 secondsboard, so it is linking to multiple MCP tools like uh tracking the order and uh
2:20:002 hours, 20 minutescancellation of the orders and all. So this client actually sits in the chatbot inside the Flipkart application. That's how it is.
2:20:092 hours, 20 minutes, 9 secondsNo, the chatbot sits inside the client.
2:20:132 hours, 20 minutes, 13 secondsSo here the client is flip card then client is flipkart. Okay. The main the main agent is the client.
2:20:222 hours, 20 minutes, 22 secondsUh okay. So the client is flip card and then that the chatbot seats and they will get the session and they will connect to the MCP tools.
2:20:312 hours, 20 minutes, 31 secondsCorrect.
2:20:322 hours, 20 minutes, 32 secondsFine. Got it. Then it will be one to many mapping right? Client will be one and uh many MCP servers. Yes.
2:20:402 hours, 20 minutes, 40 secondsFine.
2:20:412 hours, 20 minutes, 41 secondsOkay. Ainash. An uh Rohan so uh in MCP server we have all
2:20:482 hours, 20 minutes, 48 secondsthe tools uh so to call server we are using MCP client so what exactly MCT tool is doing and how different it is
2:20:562 hours, 20 minutes, 56 secondsfrom MCP client is hey you okay what is a decorator
2:21:042 hours, 21 minutes, 4 secondsuh see you're not you're not listening
2:21:122 hours, 21 minutes, 12 secondsOkay, I have this function called review code. Say yes. Yeah.
2:21:172 hours, 21 minutes, 17 secondsOkay. I need to give this tool as a access to the llm or uh lm sitting inside the client. Say yes.
2:21:262 hours, 21 minutes, 26 secondsYes.
2:21:262 hours, 21 minutes, 26 secondsTo give that access, I'm going to write at mcbp.prompt or at mcpb.tool. Okay. To make it available to the client.
2:21:352 hours, 21 minutes, 35 secondsClear? Okay.
2:21:372 hours, 21 minutes, 37 secondsOkay. So the server needs to provide the list of the tools and the way it provides it by converting that into a MCP tool. And the way we convert any
2:21:452 hours, 21 minutes, 45 secondsfunction into MCP tool is by writing at MCP tool. Clear? Okay.
2:21:492 hours, 21 minutes, 49 secondsThe moment we write at MCP tool, the input and output that I showed you on the uh dev server becomes fixed. Clear? Okay.
2:21:562 hours, 21 minutes, 56 secondsOkay. Now in the client, we call the server. Clear? Okay.
2:22:012 hours, 22 minutes, 1 secondThe moment we call the server, the first thing that I've not done here is to get the list of the tools. Clear? Okay.
2:22:072 hours, 22 minutes, 7 secondsOkay. And the list of tools are shown to the LLM in this particular format. Okay.
2:22:142 hours, 22 minutes, 14 secondsOkay. And now when you say add two numbers, it's going to take uh it's going to remember from this. Okay. This is a schema. It's going to give a particular output which is going to say
2:22:222 hours, 22 minutes, 22 secondsadd arguments and pro and these two uh outputs these two inputs. Okay. Okay.
2:22:282 hours, 22 minutes, 28 secondsI'm going to capture that. I'm going to send it to MCP server. It's going to execute whatever it wants. is going to give me a response and I'm going to take that response give it to LM for the next step. Now what is the question?
2:22:392 hours, 22 minutes, 39 secondsSorry. Now what is the question?
2:22:432 hours, 22 minutes, 43 secondsUh so so basic understanding is uh we uh this MCP tool it is uh it is telling it
2:22:502 hours, 22 minutes, 50 secondsis it like uh adding the tool to the server.
2:22:542 hours, 22 minutes, 54 secondsIt is adding the tool to the server. You can say that this is the server. So you're not adding the tool to the server. you're adding this particular
2:23:022 hours, 23 minutes, 2 secondsfunction with a decoration of MCB protocol which then goes to the client.
2:23:082 hours, 23 minutes, 8 secondsIf I if I remove this MCP tool for example then type text will not go to the LM.
2:23:172 hours, 23 minutes, 17 secondsOkay. And it can't call it. Okay. Okay. Okay. Clear.
2:23:262 hours, 23 minutes, 26 secondsYeah. Okay. Karthik.
2:23:282 hours, 23 minutes, 28 secondsSo on let's say if I am having a web service and I want to uh host as NCB service I need to do this tooling thing and then I expose it as a server now
2:23:372 hours, 23 minutes, 37 secondslet's say a third party is going to connect to my MCP service uh I need to pass in the Python the tool file as what you just showed or but when they do
2:23:462 hours, 23 minutes, 46 secondssomething like that old uh the WSDL or some swagger sort of thing which can automatically you do that or do every time you pass a sort of Python file
2:23:552 hours, 23 minutes, 55 secondsuh I've lost the last 10 so previously We used to do this bisl and the swagger files and all that, right? Swagger file.
2:24:022 hours, 24 minutes, 2 secondsYeah, like a normal resting point. We we normally pass a swagger file to our uh Yeah. The problem again is your swagger file versus my swagger file is going to be different. Then our Kevin will have a
2:24:112 hours, 24 minutes, 11 secondsdifferent swag. Then A will have a different swag. All of us will have a different swag and different way of communication and different API and different way of calling things and different responses and different time
2:24:192 hours, 24 minutes, 19 secondsto response and then LLM will sit and look at you. But then in this case I need to send this sort of Python file every time I mean uh when I want to
2:24:272 hours, 24 minutes, 27 secondsexpose my endoint of a code. So once only. Okay. Okay.
2:24:342 hours, 24 minutes, 34 secondsOkay. I have a favorite image which I want to share with all of you. We are just trying to avoid RLM not do this.
2:24:552 hours, 24 minutes, 55 secondsAll we're trying to do is to make sure LM doesn't do this. That's all. Clear.
2:25:052 hours, 25 minutes, 5 secondsIf all of us write our servers and we have different APIs, Ellen is literally going to look at you like this like what are you doing? We don't want that. Okay.
2:25:132 hours, 25 minutes, 13 secondsUh Kevin A, you're done. A okay Kevin.
2:25:232 hours, 25 minutes, 23 secondsYeah. So basically just uh uh the MCP server is uh creating a bunch of uh
2:25:322 hours, 25 minutes, 32 secondstools or APIs in terms of tools and uh the client calls the the specific uh uh
2:25:402 hours, 25 minutes, 40 secondsMCP server. It gets a list of tools and then it sends that information to LLM and LLM would tell that okay know based
2:25:492 hours, 25 minutes, 49 secondson this like uh you you should use uh X tool. Yes.
2:25:552 hours, 25 minutes, 55 secondsFrom that LCP server and then we just call that tool. Yes.
2:25:582 hours, 25 minutes, 58 secondsIt's just basically an API server wrapped around it. Correct. Instead of calling the API directly. Exactly. Okay. Okay. Thank you.
2:26:062 hours, 26 minutes, 6 secondsOkay.
2:26:082 hours, 26 minutes, 8 secondsYeah. But just now we discussed that before MC all these various integrations used people used to write the all of
2:26:162 hours, 26 minutes, 16 secondsthese correct right now also even if you're using the decorative thing that function has to be written manually
2:26:232 hours, 26 minutes, 23 secondsfunction has to be written manually for example if you just look at that blender code it just go
2:26:322 hours, 26 minutes, 32 secondsyeah that the top one execute blend code but this has to be returned by someone and that decorator has to be at
2:26:382 hours, 26 minutes, 38 secondscorrect Right. So again the manual stuff is there. So I did not get the difference that what is what was a
2:26:452 hours, 26 minutes, 45 secondsproblem before in writing integration plan.
2:26:512 hours, 26 minutes, 51 secondsYou can write the integration. problem is LLM will have to read every different kind of integration and then remember all the different
2:26:592 hours, 26 minutes, 59 secondstypes of integrations, different type of input, different type of output, different type of formats and adder to every single possible uh permutation combination that's there.
2:27:112 hours, 27 minutes, 11 secondsBut my pass your voice is cracking a lot. Oh, for
2:27:192 hours, 27 minutes, 19 secondsfor my particular application whatever I'm I will be doing personal application yeah personal application is fine we are see we are making agents that can talk to the world
2:27:262 hours, 27 minutes, 26 secondssolve cancer and go to Mars now when you're saying my personal application my four five functions no problem at all problem becomes when we have thousands and thousands and thousands of functions
2:27:342 hours, 27 minutes, 34 secondsfor example you will use telegram as a as one of the uh requirement in the course you will need to make a telegram telegram bot now what will you do in
2:27:422 hours, 27 minutes, 42 secondsthat case so we have telegram we have google we have let's say zoom we have calendar we have other services now if I ask you to make an application and you're going to say you're going to look
2:27:512 hours, 27 minutes, 51 secondsat every single integration from these people download their different files and then force the LM to uh remember that if you're calling telegram call like that if you're calling Gmail call
2:27:592 hours, 27 minutes, 59 secondslike that if you're calling Google calendar call like that and so on that's the problem we're solving
2:28:052 hours, 28 minutes, 5 secondsfour five functions no problem at all clear on this it's very important to understand we're talking about scale
2:28:142 hours, 28 minutes, 14 secondswe're talking about thousands of functions that need to be called in that case all if all the function are speaking the same language and this work needs to be done once and this work
2:28:222 hours, 28 minutes, 22 secondstoday is going to be done by claude anyways in like five minutes max
2:28:302 hours, 28 minutes, 30 secondsokay then we have a again a so when uh let's say for example Gmail
2:28:382 hours, 28 minutes, 38 secondsexpose their MCP server uh what it means is uh I am uh I can do what they are allowing me to do with the LLM right I'm
2:28:462 hours, 28 minutes, 46 secondsbut No, that means I'm still limited by what they exposing by MC. Answer is no. I already answered this.
2:28:532 hours, 28 minutes, 53 secondsBut let me again look here. Ctrl F Gmail. Now we have email MCP, right? And
2:29:002 hours, 29 minuteslet's look at other Gmail, Gmail, Gmail, Gmail. We have many many Gmails. We have MCP Gmail also. This is written by uh gone.
2:29:102 hours, 29 minutes, 10 secondsThis is written by this particular person called Timul Bio Bio. He's not Google.
2:29:182 hours, 29 minutes, 18 secondsYou can write MCP server for any API that exists in the world. This needs to be understood very very clearly.
2:29:262 hours, 29 minutes, 26 secondsOkay. Given that I have the API knowledge, how Gmail?
2:29:302 hours, 29 minutes, 30 secondsIf let's say uh raw, right? Raw will not write a API service. Uhhuh.
2:29:372 hours, 29 minutes, 37 secondsWe can't write MCP server for RAW.
2:29:402 hours, 29 minutes, 40 secondsSo what open cloud did is they uh came up with all the MCP servers for everything under the sun and put it together. So no that's what
2:29:492 hours, 29 minutes, 49 secondsno uh anthropic just wrote a protocol that why don't you take any API and wrap around this protocol so it becomes
2:29:562 hours, 29 minutes, 56 secondseasier for LM to write. MCP is just a document of how the input and output will be structured. That's all a very simple few
2:30:032 hours, 30 minutes, 3 secondslines of code. Anyone could have written it. MCP is very very simple just a decorator. That's why I started with decorator right you you could have
2:30:112 hours, 30 minutes, 11 secondswritten MCP but you should have come with this concept earlier they figured it out because they were sol trying to solve the this is all what MCP server
2:30:182 hours, 30 minutes, 18 secondsdoes right function comes in which function blender call that tool what is going to be calling the function so before the function comes in it's going to convert that function into this
2:30:262 hours, 30 minutes, 26 secondsparticular format okay call this particular function output whatever function convert to text okay
2:30:352 hours, 30 minutes, 35 secondsokay so open clock defined mcp P server for every app means right that's correct statement or oh sorry repeat that
2:30:442 hours, 30 minutes, 44 secondsuh open claw defined MCP server for every application in the laptop or machine right okay what is openclaw
2:30:532 hours, 30 minutes, 53 secondsuh it's a u agent yeah agent yeah yes so why will why will open claw write the mcp mcp is written by these
2:31:002 hours, 31 minutesdevelopers like cursor like anti-gravity openclaw can connect to these mcp servers Okay.
2:31:092 hours, 31 minutes, 9 secondsAnd you have to you have to install these MCP servers manually. Uh why don't you install open cloud today and understand?
2:31:162 hours, 31 minutes, 16 secondsOkay. Okay. Jin.
2:31:202 hours, 31 minutes, 20 secondsUh so I want to I have a basic question like uh if the query is uh to send a meeting invite at 4 p.m. with person A
2:31:272 hours, 31 minutes, 27 secondsand B. So a client would have a flexibility to uh give the input to the LLM like uh timing and a person b can be
2:31:352 hours, 31 minutes, 35 secondsgiven into the resources or what should be given to the LLM what should be uh taken at as using as a resources or
2:31:432 hours, 31 minutes, 43 secondslm have a function that can trigger at 4 p.m. If there's no function that triggers at 4 p.m. that feature is not possible.
2:31:522 hours, 31 minutes, 52 secondsOkay thank you. Okay. Nan.
2:31:572 hours, 31 minutes, 57 secondsYeah. Uh, so I just wanted to know this MCP client is just a way to uh wrap that uh maybe to to to say that I will only
2:32:062 hours, 32 minutes, 6 secondsinteract with uh with a given server in this specific way. Exactly. Maybe if I Okay. Exactly Kevin.
2:32:132 hours, 32 minutes, 13 secondsUh so who would be hosting the MCP server? Let's say uh if you're going to consume for Google, Telegram, uh it
2:32:202 hours, 32 minutes, 20 secondswould make sense to consume these MCP servers hosted by these uh the actual providers, right?
2:32:272 hours, 32 minutes, 27 secondsMCP server. Okay. Is are you calling a function once? Uh no, could be multiple times.
2:32:372 hours, 32 minutes, 37 secondsDo you need a constant connection? Okay.
2:32:462 hours, 32 minutes, 46 secondsNow I'm asking a question. Do you need a constant connection or you calling it once? Uh no no constant connection. I mean we we
2:32:532 hours, 32 minutes, 53 secondscan call it multiple times but uh yeah if it is not a constant connection then you can download a Python file and run the server. If it is a constant
2:33:012 hours, 33 minutes, 1 secondconnection someone needs to provide that as a SSC service.
2:33:062 hours, 33 minutes, 6 secondsOkay. So so would so let me ask you the other way around. So for uh uh for all the scenarios for connecting for using
2:33:152 hours, 33 minutes, 15 secondsMGP uh would we be would there be any scenario where we would need constant connection or uh it would always be
2:33:232 hours, 33 minutes, 23 secondslot of scenarios lot of scenarios whenever you need a streaming connection you'll need okay so it would be a mix of both right
2:33:322 hours, 33 minutes, 32 secondsalways be a mix of both yes okay can can you can you help me understand like what would be a scenario where we would need like constant streaming and live stock market data.
2:33:452 hours, 33 minutes, 45 secondsOkay. Live YouTube stream. Okay.
2:33:492 hours, 33 minutes, 49 secondsOkay. See what's I think like most of the scenarios that I'm thinking is like maybe one time scenario like okay connecting to your Gmail or uh your
2:33:582 hours, 33 minutes, 58 secondscalendar. Uh so those will be like oneoff connections.
2:34:012 hours, 34 minutes, 1 secondYeah. Camera no camera connection for example you're doing some sort of security monitoring. You need a constant camera stream. Mhm.
2:34:092 hours, 34 minutes, 9 secondsSo think of SS is like like camera uh at your building or at your house is always streaming. You decide when when you want to connect and uh disconnect but that
2:34:172 hours, 34 minutes, 17 secondswill that service is always on like it is in security camera if you have installed any. Mhm. Okay.
2:34:242 hours, 34 minutes, 24 secondsSo in that scenario we would be kind of connecting to MCP servers which are hosted by those providers streaming. Yes.
2:34:322 hours, 34 minutes, 32 secondsOkay.
2:34:332 hours, 34 minutes, 33 secondsOkay. Last two questions before I move to L&M. Uh thank you. Thank you uh Rohan. So Rohan I understand. So from the uh you have
2:34:402 hours, 34 minutes, 40 secondsshown us the awesome ser mcb servers. So from our client uh so from our terminal from anti-gravity or anything ko
2:34:482 hours, 34 minutes, 48 secondsanything. So uh you have downloaded the server.py file and we have to download it and we have to put it in our terminal and from our client if we call this uh
2:34:572 hours, 34 minutes, 57 secondsserver then we can so this is a general procedure to connect to any MCP server. Um right. Yeah.
2:35:042 hours, 35 minutes, 4 secondsOkay. Thank you.
2:35:062 hours, 35 minutes, 6 secondsAll right. Okay. Now let's move to actual agents. So I have two of them. I have one connected to Gemini, the other
2:35:132 hours, 35 minutes, 13 secondsconnected to Ola. Let's start with the Gemini first.
2:35:232 hours, 35 minutes, 23 secondsOkay.
2:35:262 hours, 35 minutes, 26 secondsNow here we have agentic loop over example MCP server. The agent the example server that we wrote earlier. Earlier we ran it with MCP dev example.
2:35:352 hours, 35 minutes, 35 secondsHere I'm going to be calling within the client itself. This is a client, right?
2:35:382 hours, 35 minutes, 38 secondsSo this whole thing is harness. This whole thing is your agent. LM is a part of it. MCP server is a part of it. MCP
2:35:452 hours, 35 minutes, 45 secondsserver provides tools. When the tools are given to LM, it becomes an agent.
2:35:492 hours, 35 minutes, 49 secondsRight? But what is agent? This whole code is a agent. You need to understand that. Harness is basically us connecting different things together. That's why sometimes we call it a harness also.
2:35:582 hours, 35 minutes, 58 secondsOkay. Uh the model picks tool from MCB server and we execute them. We have to execute. model cannot execute model can only tell us I want to call this
2:36:062 hours, 36 minutes, 6 secondsparticular tool and we're going to feed the result back to the ln to understand what is it what is it that wants to do next and if it gives us final answer
2:36:152 hours, 36 minutes, 15 secondsthen we know that it's a final answer we stop the loop right so the running of the loop is controlled by this particular code this code is also called
2:36:222 hours, 36 minutes, 22 secondsagent agentic orchestration this is what lang chain is this is what uh clot code is this is what anti-gravity is this is
2:36:292 hours, 36 minutes, 29 secondswhat cursor is this one single file is a very very rudimentary example example of all the agents that we're going to be building in future.
2:36:362 hours, 36 minutes, 36 secondsSo task chosen on purpose. So the model needs three tools. Uh it need to write a file, it need to read a file and need to edit a file. So from the new code in
2:36:452 hours, 36 minutes, 45 secondsyour case, you don't have you directly have the code. We're going to be running u run agent agentic mcpus or just python. Gemini is already in the env
2:36:542 hours, 36 minutes, 54 secondsfile for me. So I'm going to be using 3.1 flash light preview max iteration 6 sleep 5 second. So I sleep 5 second
2:37:012 hours, 37 minutes, 1 secondbefore I call lm. So anytime I call it, I'm not going to go out of because it might crash and it might call again, right? That can happen. So this is one single thing I use to make sure that I don't go out of the rate limits I have.
2:37:122 hours, 37 minutes, 12 secondsLM time out 15 seconds. I'm going to wait for 15 seconds and say okay, done.
2:37:152 hours, 37 minutes, 15 secondsI'm not connected. So first thing is we connect to the client which is the Geni Gemini. So we have a client now and I'm
2:37:242 hours, 37 minutes, 24 secondsgenerating with timeout. So when I send a request, I wait for 15 seconds and then I come back come back and say okay, it's not connecting. Now describe the
2:37:312 hours, 37 minutes, 31 secondstools is going to enumerate. It's going to get the uh input schema and it's going to get the properties and it's going to print some things. I'm going to go inside the code and show you also
2:37:392 hours, 37 minutes, 39 secondswhat happens. Uh course we're going to make sure that when we are getting integer we are getting the int value.
2:37:472 hours, 37 minutes, 47 secondsWhen we have a number we converting that in float. When we have array we are going to be converting that into anal value. And we have a boolean we're going to convert that in true one or yes.
2:37:552 hours, 37 minutes, 55 secondsOkay. First thing this is the main code again because we're connecting to something that is going to be a synchronous nature. Our main is going to be a sync. Inside that I have studio server parameter like we had last time.
2:38:072 hours, 38 minutes, 7 secondsI'm going to say Python and example MCP server here. It could be Blender server. It can be zoom server. Anything we want.
2:38:132 hours, 38 minutes, 13 secondsOkay. Then I'm going to initialize the connection. This is where we initialize the connection. Once the connection is done, we're going to get the print command that I have connected. Till now
2:38:212 hours, 38 minutes, 21 secondsLM is not involved. First thing I do as I told you earlier, we're going to get session.list tools. This is what we did on the UI also, right? I clicked on the
2:38:292 hours, 38 minutes, 29 secondslist tools. I got the list of all the tools. I'm going to get the tools and I'm going to get the describe tools. If you see describe tools here, this is a
2:38:372 hours, 38 minutes, 37 secondsformat in which I like to restructure the output of MCP tools to give it to the LLM. We're going to see that output also.
2:38:462 hours, 38 minutes, 46 secondsAnd I'm going to just print them. This is for us, not going to LM yet. Now, here is a SIM prompt. You are a file manipulation agent working inside a
2:38:552 hours, 38 minutes, 55 secondssandbox MCP server. You solve task by calling tools one at a time and observing the results. The available tools to you are tool description which
2:39:042 hours, 39 minutes, 4 secondsI'm going to be uh capturing from the describe tools. Respond with exactly one line in one of the
2:39:132 hours, 39 minutes, 13 secondsin one of the one of the following two formats. Function call tool name argument one argument two. Final call short natural language summary of what
2:39:212 hours, 39 minutes, 21 secondsto do. Rules provide arguments in the exact order of the tools parameter. Do not invent tools that are not listed over. All of this by the way useless.
2:39:292 hours, 39 minutes, 29 secondsThis all of this was required last year January but now no all the models are really good. But if you're using something on a smaller uh model or a weaker model then this will be required.
2:39:412 hours, 39 minutes, 41 secondsOkay. Now task create a file called greetings.txt in the sandbox. Let's change from greetings to hello.xt
2:39:502 hours, 39 minutes, 50 secondsbecause already there and write hello tsi.
2:39:572 hours, 39 minutes, 57 secondsCreate a file called hello.txt in the sandbox with the cont with the content hello tsi. Then read it back to confirm.
2:40:042 hours, 40 minutes, 4 secondsThen edit it so it becomes hello all students.
2:40:162 hours, 40 minutes, 16 secondsI'm sorry. Okay,
2:40:262 hours, 40 minutes, 26 secondsthen edit it back. So, hello TSI becomes hello all students. Finally, give a final answer. This is my request to the LM. Now, in the history, I'm going to
2:40:352 hours, 40 minutes, 35 secondsstore all of what has happened. Same thing we did in last session. Now I'm going to look at max iteration which I kept at six. Iteration number is going
2:40:432 hours, 40 minutes, 43 secondsto be printed. I'm going to join the history because whatever has happened I'm going to keep on give it to LM.
2:40:472 hours, 40 minutes, 47 secondsRemember we are at a stateless LM where the Gemini will not remember what happened last step. The prompt the task the previous step and what is the next
2:40:552 hours, 40 minutes, 55 secondssingle action is what we're going to be giving to the LM. So this becomes an actual prompt that goes to the LM every time. Now we're going to sleep for 5 seconds to make sure that I'm not
2:41:032 hours, 41 minutes, 3 secondsdisturbing my rate limits. Then once the sleep is done, I'm going to try and get a response. Try and catch we saw earlier. Try and get the response from
2:41:122 hours, 41 minutes, 12 secondsthe uh client. Remember generated with timeout. We're waiting for five 15 seconds. If I time out, I'm going to say lm timed out. Something is wrong.
2:41:202 hours, 41 minutes, 20 secondsOtherwise, I'm going to get the response back. If I get the response, I'm going to get the response text and I'm going to strip the split lines and strip zero.
2:41:282 hours, 41 minutes, 28 secondsAll of this is something your uh clot code will be able to do easily. We're going to get a response printed not required in the final LLM agent calls.
2:41:362 hours, 41 minutes, 36 secondsIf it starts with final answer agent done, we're just going to print the answer. If it start with function call, I'm going to get the we we are just breaking it here because we don't want
2:41:442 hours, 41 minutes, 44 secondsit to do anything. We are just saying uh unexpected response format stopping here. Right? If it's not function call,
2:41:522 hours, 41 minutes, 52 secondsif it is not if it is final answer, done. If it is not function call, something is wrong. Otherwise, it is function call. If it is function call, I'm going to split the text. I'm going to get the call uh for P in call.splits.
2:42:042 hours, 42 minutes, 4 secondsI'm going to get the P which is parameter if you remember right we ask it to give us response back in tool name parameter parameter. I'm going to
2:42:122 hours, 42 minutes, 12 secondsextract the parameters. I've extracted a part and I've extracted a second part if it is there. I'm going to call the tool.
2:42:192 hours, 42 minutes, 19 secondsTool is going to be there in the function name that we described above.
2:42:222 hours, 42 minutes, 22 secondsAnd here we have the props which is the input schema sorry input parameter that
2:42:302 hours, 42 minutes, 30 secondsI need to add. I'm going to coers them to make sure that they are in the right format. They're integers and they're all of this is something that is is required
2:42:372 hours, 42 minutes, 37 secondsto be done on the client side. Then I'm going to be calling the session which is my MCP client uh MCP server. I'm going
2:42:442 hours, 42 minutes, 44 secondsto do a tool call. Function name I already extracted. I'm going to send the arguments and results are here. I'm going to store the results in the
2:42:522 hours, 42 minutes, 52 secondspayload and I'm going to append the payload back into the history and the cycle will repeat. Now,
2:43:022 hours, 43 minutes, 2 secondscan someone tell me uh what do I write here
2:43:112 hours, 43 minutes, 11 secondsso I can actually go through the code line by line? Anyone remembers session two and three? Session three.
2:43:192 hours, 43 minutes, 19 secondspoint. Fine.
2:43:292 hours, 43 minutes, 29 secondsAll right. Now, let's run this MCP use.
2:43:442 hours, 43 minutes, 44 secondsOkay. So, we printed connected to MC server. Now I'm pressing N connected to the example server. This
2:43:522 hours, 43 minutes, 52 secondsline has happened. Okay. Now this line will happen. Let's let's press N which is this line was executed and uh
2:44:012 hours, 44 minutes, 1 secondresults are now stored in the tools. Now let's see what is there in the tools.
2:44:052 hours, 44 minutes, 5 secondsAll this in tools right? I've sent all the tools that were there in the MCP example MCP server. This is what is captured and given. You can already see
2:44:132 hours, 44 minutes, 13 secondshow dense this is. Now when you think about and this is just like 12 12 13 functions we wrote now if you talk about
2:44:202 hours, 44 minutes, 20 secondsblender Gmail uh Google drive all of that would have been sent right so it will be very tricky so let's press N now
2:44:302 hours, 44 minutes, 30 secondsprint loaded length of tools which is this line but let's see what is the tool description because tool description is going to be sent also right so we are
2:44:372 hours, 44 minutes, 37 secondsdoing tools_deesc this is description that we sent much more easier way for LLM to understand
2:44:452 hours, 44 minutes, 45 secondsright add a number b number add two numbers then the function to square root a number square root of a number this
2:44:532 hours, 44 minutes, 53 secondsbecomes very simple and this is what we send I can send the whole mcp output also but generally I'm keeping things simple right now to make sure that it works with simpler lm in future we'll
2:45:012 hours, 45 minutes, 1 secondjust dump everything and we're going to make sure that works properly there so and let's look at len of tools to see
2:45:092 hours, 45 minutes, 9 secondshow many tools are there we're sending 20 functions so example mcgp server has 20 functions that we are sending. Okay, let's press N. So next is system prompt.
2:45:192 hours, 45 minutes, 19 secondsThis is the whole thing that is being looked at right now. So let's press N. System prompt is done.
2:45:272 hours, 45 minutes, 27 secondsThis is a full system prompt. Okay. So system prompt.
2:45:502 hours, 45 minutes, 50 secondsOkay, so this is what is sent to LM.
2:45:532 hours, 45 minutes, 53 secondsYou are a file manipulation agent working inside sandbox MCV server. You solve the task by calling one to add at the number and observing the results
2:46:002 hours, 46 minutesavailable tools are. So now to look at it properly, I'm just going to copy this.
2:46:252 hours, 46 minutes, 25 secondsOh, backspace is not working. Okay.
2:46:552 hours, 46 minutes, 55 secondsIt becomes so difficult for me sometimes to tell Charg what I want.
2:47:052 hours, 47 minutes, 5 secondsThank you. Okay. So this is this is exactly what is sent to RLM. You're a file manipulation agent working inside a sandbox server. You solve task by
2:47:132 hours, 47 minutes, 13 secondscalling one tool at a time and observing the results. The available tools are this is how we send the list of all the tools that are there. Okay, we kept
2:47:202 hours, 47 minutes, 20 secondsthings very simple for LM. Right now we following still the old old part. Next session we're going to this part and just dump the MCP as I said because
2:47:282 hours, 47 minutes, 28 secondsthat's going to be much more easier. Now the reason I've not done that, the reason I've not using the full MC power is because I'm trying to tell you
2:47:352 hours, 47 minutes, 35 secondssomething very specific here. You see the complexity I've added in the code, the complexity I've added is I'm taking the list of tools and I'm writing
2:47:432 hours, 47 minutes, 43 secondsspecific functions to course my outputs, right? Co my inputs that are going then I'm describing my tools in such a way
2:47:502 hours, 47 minutes, 50 secondsthat can I can actually feed it to the LM. All of this is not required.
2:47:562 hours, 47 minutes, 56 secondsYou can take it as an assignment. Get rid of describe tools. Get rid of course and just send exactly what you get here
2:48:032 hours, 48 minutes, 3 secondstools. You can send exactly just the tools to the LM it will understand everything in the input and output. Now because I'm forcing it this is the old
2:48:112 hours, 48 minutes, 11 secondsway of doing it. If you're not using MCP server and normal API this is the this is how the code will be written. You'll do that then once the LM output comes in
2:48:202 hours, 48 minutes, 20 secondsyou're going to extract all of this also. You saw the code here that we wrote. All of this not required.
2:48:282 hours, 48 minutes, 28 secondsAll of this complication is not required. Extracting the parameters, extracting all the stuff. But I'm keeping it to just because we are following from the last session to make
2:48:362 hours, 48 minutes, 36 secondssure you understand the complexity of not ading to MCB protocol.
2:48:422 hours, 48 minutes, 42 secondsWe we have a list history max iteration and let me just press C. Now we're calling the lm first.
2:48:592 hours, 48 minutes, 59 secondsYeah, I expected. Okay.
2:49:192 hours, 49 minutes, 19 secondsOkay. So first starteration because I'm running on uh gamma 4 here I don't need to wait slipping 0 seconds before the lm
2:49:262 hours, 49 minutes, 26 secondscall it calls the llm sees okay what what is lm output function call write file called greetings txt hello Rohan um
2:49:352 hours, 49 minutes, 35 secondsold code then iteration two read the file we got hello Rohan then third call edit file greetings txt hello change
2:49:442 hours, 49 minutes, 44 secondshello with hi and edited greeting txt sleeping 0 second before final call final answer is created greeting txt
2:49:522 hours, 49 minutes, 52 secondswith hello Rohan verified it content uploaded updated it to say hi and if you go in the sandbox and if you click here
2:49:592 hours, 49 minutes, 59 secondswe're going to see hi okay now let me go back here and let's see what all we had
2:50:062 hours, 50 minutes, 6 secondswe had mouse move and uh screen size we had run command no delete then we had
2:50:142 hours, 50 minutes, 14 secondsfetch URL okay fetch URL is there then we And
2:50:212 hours, 50 minutes, 21 secondslet's look at fetch URL only. Fetch URL only. Okay, fine. Let me go back to here. All this can be on the chat, but let me just write it here.
2:50:322 hours, 50 minutes, 32 secondsTask visit.
2:50:392 hours, 50 minutes, 39 secondsWhat can be a small website? Uh news.y Y
2:50:462 hours, 50 minutes, 46 secondscomment.com and
2:50:562 hours, 50 minutes, 56 secondsget the titles of the top 10 posts.
2:51:042 hours, 51 minutes, 4 secondsCreate a file called y comment.txt. txt
2:51:132 hours, 51 minutes, 13 secondsand save the titles in it. Finally, give the final answer.
2:51:222 hours, 51 minutes, 22 secondsFinally, confirm the contents.
2:51:282 hours, 51 minutes, 28 secondsNot finally, confirm the contents of the file
2:51:392 hours, 51 minutes, 39 secondsand get the final answer. Okay, now let's run this
2:51:562 hours, 51 minutes, 56 secondsremember this is the uh this is what is there on the SATP right and we have a 2,00 uh limit also so probably that
2:52:052 hours, 52 minutes, 5 secondsneeds to be longer or smaller but it's a small pace so I'm hoping that it can get some good answer.
2:52:162 hours, 52 minutes, 16 secondsAnd you can see it called it twice. It's getting confused already.
2:52:332 hours, 52 minutes, 33 secondsIt failed.
2:52:442 hours, 52 minutes, 44 secondsAh, okay. Prompt needs to change here.
2:52:472 hours, 52 minutes, 47 secondsSee, I we asked it to always respond by uh always respond by a function call.
2:52:552 hours, 52 minutes, 55 secondsSo, prompt change required here.
2:54:012 hours, 54 minutes, 1 secondLet's see if uh Gemini is back. Uh
2:54:192 hours, 54 minutes, 19 secondsOkay. In the meantime, Sanja Roan, when you mentioned like you know
2:54:272 hours, 54 minutes, 27 secondsyou can remove all the complexities in the code. So what exactly you meant? Can you give an example?
2:54:352 hours, 54 minutes, 35 secondsThis function not required. this function not required and all of this is not required.
2:54:472 hours, 54 minutes, 47 secondsUh because LLM are uh intelligent enough to understand all these things.
2:54:532 hours, 54 minutes, 53 secondsBecause LMS are intelligent understand all these things.
2:54:572 hours, 54 minutes, 57 secondsUh why it is not required? Actually I couldn't follow that part. Oh because this is what MCP does. MCP structures all of this.
2:55:062 hours, 55 minutes, 6 secondsOkay. Got it. Thank you. Okay.
2:55:112 hours, 55 minutes, 11 secondsI had a similar question. So MCP handles this part of uh uh again uh converting
2:55:182 hours, 55 minutes, 18 secondsit into the required form calling the function all that the MCP um client or server does client client.
2:55:272 hours, 55 minutes, 27 secondsOkay. Um uh one more thing. So um you showed us that Yeah, I'm sorry. MCP server handles all
2:55:352 hours, 55 minutes, 35 secondsof this and the client just need to u take the content extract the content in a specific way and provide it to a server.
2:55:422 hours, 55 minutes, 42 secondsAh okay. Okay. Um second thing uh we saw that GitHub that awesome set of MCP
2:55:502 hours, 55 minutes, 50 secondsservers. Do we always um download the server and run it or uh is is it possible that these guys uh big
2:55:592 hours, 55 minutes, 59 secondsenterprises are running the servers somewhere and we just call call them you don't have to always run it right
2:56:072 hours, 56 minutes, 7 secondsfor constant connections we uh someone would provide it to you for one time use we need to download and use
2:56:142 hours, 56 minutes, 14 secondswhat if it is too huge and you're not able to host it yourself does I irrespective of whether it's streaming or one time.
2:56:232 hours, 56 minutes, 23 secondsNo, it's it's a technical requirement.
2:56:252 hours, 56 minutes, 25 secondsIf someone is streaming something, they have to host it because it has to be always running on something, right?
2:56:302 hours, 56 minutes, 30 secondsTelegram is always running. So if you want to talk to talk on Telegram, you have to connect to something that is always running. And uh who can always
2:56:382 hours, 56 minutes, 38 secondsrun Telegram? Telegram. Who can always run Google? Google.
2:56:422 hours, 56 minutes, 42 secondsYeah. Like Google run Google APIs always. And when I need to make a call like rest API can't I make a call I
2:56:512 hours, 56 minutes, 51 secondsmeaning the client MCP client makes a call and get when you need to connect to something once in a while you will be it's okay
2:56:592 hours, 56 minutes, 59 secondsfor you to do it but when you if you're connecting to something that requires uh constant connection like stock market data or let's say a video feed then they need to provide a constant connection.
2:57:122 hours, 57 minutes, 12 secondsNo, I'm not even coming to constant connection or one time. Why should I download that and run it? Like you make a rest API call.
2:57:222 hours, 57 minutes, 22 secondsWho makes the rest call? Huh? Sorry. Who will make the rest API call? Client. Why?
2:57:292 hours, 57 minutes, 29 secondsNo to rest API call to what? Some server, right? Yeah.
2:57:332 hours, 57 minutes, 33 secondsWhy will Blender provide you a free service?
2:57:362 hours, 57 minutes, 36 secondsBecause I'm maybe I'm their customer. I have a subscription. No, Blender is free open source.
2:57:432 hours, 57 minutes, 43 secondsNo, I mean someone I I've subscribed to something. So why they should provide that only thing uh there may be I mean
2:57:522 hours, 57 minutes, 52 secondswhy should I trust code on some GitHub server and run it? It comes with lot of complexities. I
2:58:002 hours, 58 minutesI don't know how to I don't know how to answer that question. There are opensource software that everyone uses.
2:58:042 hours, 58 minutes, 4 secondsUh companies will want not to provide you a server to save their cost. If you want them to provide then they can charge you into it but I don't know who
2:58:112 hours, 58 minutes, 11 secondsis doing it. Everyone provides a free uh MCP and it's just a single uh file that needs to be downloaded and connected.
2:58:192 hours, 58 minutes, 19 secondsOkay. Okay. Thank you. Uh SPN.
2:58:252 hours, 58 minutes, 25 secondsSo uh Rohan so there so for example there is a MCP server for GitHub right
2:58:322 hours, 58 minutes, 32 secondsuh that that runs something in docker on my machine but GitHub is something which is running 24/7 on so the MCP server in
2:58:412 hours, 58 minutes, 41 secondsthis case is just a middleware which translates uh stuff from my agent to actual GitHub
2:58:492 hours, 58 minutes, 49 secondsAPI is that it that's so where is MCP server exactly Okay.
2:58:552 hours, 58 minutes, 55 secondsMCB server is on your computer, right? So, so basically uh that MCP server is just uh translating my request for GitHub, right?
2:59:042 hours, 59 minutes, 4 secondsThat's correct.
2:59:062 hours, 59 minutes, 6 secondsOkay. And when you said that we can remove the tools uh description, all these things from here we we there is
2:59:122 hours, 59 minutes, 12 secondsstill uh the uh tool annotations and uh doc strings all of these are still provided to the LLM, right? For choosing the tool.
2:59:212 hours, 59 minutes, 21 secondsThat's correct.
2:59:232 hours, 59 minutes, 23 secondsWe we just don't mention it in the prompt. That's correct. Okay. Thanks. Okay.
2:59:312 hours, 59 minutes, 31 secondsSo in the example that you are showing us um where you have three steps of uh getting the for example the second hama
2:59:382 hours, 59 minutes, 38 secondsexample that you have um visit a website find out the top 10 stories and then
2:59:452 hours, 59 minutes, 45 secondscreate a file out of it. So here we are like um maybe there are like at least three calls to the LLM from the um agent
2:59:542 hours, 59 minutes, 54 secondsthat we have created. So each time you kind of send the answers or the content from the last call response and your
3:00:023 hours, 2 secondscall responses each time and the request keeps getting bigger and bigger with each call. Yes, that's a contact.
3:00:123 hours, 12 secondsOkay. So first call you send me you send it the uh website name and then the um MCP details of and the entire system
3:00:213 hours, 21 secondslike maybe have like 20 MCP tools. So 20 plus the website and the response in the next call you send the content of the
3:00:293 hours, 29 secondswebsite the website name and again the 20 calls. Yes. Okay. Thank you.
3:00:373 hours, 37 secondsThat is why the context will become very important for us. Okay. Go ahead.
3:00:463 hours, 46 secondsYeah. So, uh, so I've been using cursor.
3:00:493 hours, 49 secondsUh, uh, the problem is I mean I just want to understand one concept. So, here we are exposing an MCP and uh then we are uh
3:00:583 hours, 58 secondstaking the chain of uh tools that are being exposed describing them and then making the calls uh manually via the
3:01:063 hours, 1 minute, 6 secondsclient. Right? That's the workflow that we have built. But in case let's say if I use cursor as the client and uh let's
3:01:133 hours, 1 minute, 13 secondssay if I talk about Vicki or maybe playright any of the you know MCPS that are publicly available when I integrate
3:01:213 hours, 1 minute, 21 secondsthem I do not have to describe those tools and if I put a query then how does it get the list of tools and how does
3:01:283 hours, 1 minute, 28 secondsLLM get to know that okay for this I have to go to the playright or wick MCP to fetch the answer
3:01:363 hours, 1 minute, 36 secondsmoment install MCP inside a cursor Sir you have done exactly what we have done manually here. So that that's the job of the agent harness or agentic system right?
3:01:463 hours, 1 minute, 46 secondsMhm.
3:01:473 hours, 1 minute, 47 secondsSo the what is the question? Cursor is doing exactly what we just did. So how is cursor?
3:01:523 hours, 1 minute, 52 secondsMy question is how how uh so cursor in inherently uses an element. Let's say I'm exposed to set or highq right?
3:02:003 hours, 2 minutesSo how how if I'm integrating a playright mcp for example they're all in a list of tools. So based
3:02:063 hours, 2 minutes, 6 secondson my question how how yeah please all what we did is what cursor will do extract all the tools list all the tools and then send it to sonet.
3:02:163 hours, 2 minutes, 16 secondsSo that client code is part of cursor you mean cursor is client.
3:02:213 hours, 2 minutes, 21 secondsMhm. So all that orchestrations is already written in it. Correct. Cursor is the agent.
3:02:273 hours, 2 minutes, 27 secondsOkay. And how does it distinguish whether it's a playright question go should go to playright MCP versus a normal question.
3:02:343 hours, 2 minutes, 34 secondsYeah. Skills. That's where anti-gravity uh cursor code or clot code and cursor they are fighting with each other. How can they maintain the context better?
3:02:423 hours, 2 minutes, 42 secondsHow can they only expose the tools that are required?
3:02:443 hours, 2 minutes, 44 secondsOkay. So you mean the skills is also part of that cursor client, right? Correct.
3:02:503 hours, 2 minutes, 50 secondsOkay. And one more question I have uh Ran. So regarding that constant streaming that we discussed, right? So
3:02:563 hours, 2 minutes, 56 secondshow I understand it is uh let's say if I'm talking about a video streaming platform, right? So in that case uh do
3:03:043 hours, 3 minutes, 4 secondswe still need a MCP server running all the time versus a YouTube API running all the time?
3:03:123 hours, 3 minutes, 12 secondsOkay, YouTube API served through a ser serve through MCP server, right? So uh MCP server can still be
3:03:193 hours, 3 minutes, 19 secondsstandalone, can't it be? But the go uh YouTube API should be constant in is what I understand because it's still a
3:03:263 hours, 3 minutes, 26 secondsstill a standalone request that I'm making to MCP server. What is MCP? So MCP is directing me to API.
3:03:343 hours, 3 minutes, 34 secondsNo, what is MCP? You're talking I'm not even using the word MCP. What is MCP?
3:03:403 hours, 3 minutes, 40 secondsIt's a protocol to describe the list of tools that a uh service is exposing.
3:03:463 hours, 3 minutes, 46 secondsCorrect. So now if the tools internally are one time, then it's one time. If the tools internally are constant, streamable, constant connection based,
3:03:533 hours, 3 minutes, 53 secondsit needs to be constant connection based. It's just set up. Yeah, it's a wrapper.
3:03:593 hours, 3 minutes, 59 secondsSo that's what I'm saying. Uh, so MCP can still be standalone, right? The underlying API has to be constant. Isn't should be the case.
3:04:063 hours, 4 minutes, 6 secondsUnderline API has to be constant. What do you mean of constant?
3:04:103 hours, 4 minutes, 10 secondsConstant means constantly streaming or constantly available. Uh, okay. If I stream it to MCP server which is not constant in your word, then how do I pass it on?
3:04:213 hours, 4 minutes, 21 secondsA streaming server passes data to MCP server which is not streaming. Then how do I stream it to the user?
3:04:283 hours, 4 minutes, 28 secondsNo this what I'm saying is uh does MCP server has to be constant or not is what my question is in this case YouTube streaming for example you answer my question YouTube is
3:04:373 hours, 4 minutes, 37 secondsstreaming to a server which is not streaming further you understand the problem
3:04:443 hours, 4 minutes, 44 secondswhat is the problem my problem is uh whether MCP server has to be constant or not definitely YouTube has to be constant
3:04:523 hours, 4 minutes, 52 secondsfirst don't use the constant word it's confusing me I'm very dyslexic I think you probably means the MCP server can be locally downloaded and kept whereas the
3:05:013 hours, 5 minutes, 1 secondYouTube API can be running online, right? Yeah, that you can do. Yes. Yeah. Yeah. Okay. But it is a streaming server locally.
3:05:103 hours, 5 minutes, 10 secondsYou you need to say yes to that. Uh YouTube server you mean? Or the MCP? MCP server has to be streaming locally.
3:05:183 hours, 5 minutes, 18 secondsYeah. Yeah. Absolutely. Yeah. Yeah. Then you're cool. Yeah. Okay. Thanks. Okay. Okay.
3:05:253 hours, 5 minutes, 25 secondsSo in this case uh in this example that you shared right so there's one NC MPC MCP server which has say 20 tools. Uh
3:05:333 hours, 5 minutes, 33 secondsbut let's say if we are using say five MCP servers uh and each one of them has say 20 tools say 100 tools. Yeah,
3:05:403 hours, 5 minutes, 40 secondssession six is where we are going to touch upon first time the multiMCP server and session around 9 10 we're going to touch upon thing called skills
3:05:483 hours, 5 minutes, 48 secondswhere we're going to decide slowly which skill need to be provided and each skill is a MCP server.
3:05:543 hours, 5 minutes, 54 secondsOkay. So right now essentially we we we don't need to provide all the MCP server tools to the agent.
3:06:043 hours, 6 minutes, 4 secondsCorrect. So what what will happen and that's where the orchestration is going to come into picture. We're going to tell our main agent that you have these skills. This is Gmail skill. This is Zoom skill. This is YouTube skill. Okay.
3:06:163 hours, 6 minutes, 16 secondsWhenever something like this come in, spawn a small another agent with a Gmail skill.
3:06:213 hours, 6 minutes, 21 secondsSo we ask this guy for example, our main agent that hey can you check my Gmail account.
3:06:263 hours, 6 minutes, 26 secondsNow if this guy opens the MCP server, it it gets the whole context gets bloated. Yeah.
3:06:333 hours, 6 minutes, 33 secondsRight. So we so it's going to be that uh agent is also going to be concerned.
3:06:363 hours, 6 minutes, 36 secondsIt's going to know I'm not going to do that. I'm going to spawn a temporary agent or temporary LM with the Gmail scale. It's going to fetch all the content and give it to me. So I never
3:06:443 hours, 6 minutes, 44 secondslook at the tools that are there in Gmail. My sub agent is going to do that's the this these are the set of skills. These are the sub aents.
3:06:533 hours, 6 minutes, 53 secondsGot it. The sub agent basically is like we don't want to put the context and then specialize into that. So the uh so
3:06:593 hours, 6 minutes, 59 secondsthe LLMs are more focused on working in that uh narrowed context. Correct.
3:07:093 hours, 7 minutes, 9 secondsOkay. Uh, Sra Roh. So, a agents are nothing but the
3:07:163 hours, 7 minutes, 16 secondsclients, right? That makes the call like uh in the uh suppose cloud code we
3:07:243 hours, 7 minutes, 24 secondsare making some calls and it has some MCP like suppose um it has access to
3:07:313 hours, 7 minutes, 31 secondsGmail MCP, right? So whatever we are writing in the uh this agent or the
3:07:383 hours, 7 minutes, 38 secondscloud uh cloud code so that is the client call that we are making to the MCP of Gmail. Yes. Clock your client is agent. Agent is client.
3:07:493 hours, 7 minutes, 49 secondsA agent is client. Okay. Now the next thing is there is actual Gmail. I think so it's a punima's thing also like there
3:07:573 hours, 7 minutes, 57 secondsis an actual Gmail which is sitting there and there is a Gmail MCP which we have locally downloaded it right.
3:08:063 hours, 8 minutes, 6 secondsSo this MCP has a server and a client.
3:08:093 hours, 8 minutes, 9 secondsUh so client we understood server contains the list of tools that is provided. uh so that we can like
3:08:163 hours, 8 minutes, 16 secondscontains a list of cools so that we can uh connect with Gmail right now when we are one thing which is confusing me is
3:08:253 hours, 8 minutes, 25 secondswhen you are telling like you know download it locally like the server and the Gmail that is actually sitting
3:08:333 hours, 8 minutes, 33 secondslike whatever Google provides the Gmail so that what does Google provide
3:08:413 hours, 8 minutes, 41 secondslike basically it provides uh like It has Gmail has its own server right?
3:08:473 hours, 8 minutes, 47 secondsNo, no, you're not answering the question. What does it provide through the server API?
3:08:513 hours, 8 minutes, 51 secondsAPI like we have the API calls server the MCB server locally will wrap that API online command with MCP. That's all.
3:09:013 hours, 9 minutes, 1 secondYeah, it is it is basically in the uh like pre AI world we used to do the rest API calls to Gbain. Now we will be doing with the MCP.
3:09:113 hours, 9 minutes, 11 secondsExactly.
3:09:133 hours, 9 minutes, 13 secondsRight now the thing is that uh like if we have to hit that Gmail we are
3:09:193 hours, 9 minutes, 19 secondsactually hitting the actual Gmail server right like not something which is running in local
3:09:263 hours, 9 minutes, 26 secondscorrect okay so uh so this server what we are
3:09:323 hours, 9 minutes, 32 secondstalking about MCP is just the instead of a it's a wrapper uh on top of the rest
3:09:403 hours, 9 minutes, 40 secondsAPI calls that we are doing similar kind of authentication and everything needs to be done to call the actual Gmail server.
3:09:483 hours, 9 minutes, 48 secondsYes. Okay.
3:09:503 hours, 9 minutes, 50 secondsSession is so the MCT server and the actual Gmail server are two different things for us, right?
3:09:573 hours, 9 minutes, 57 secondsThat's correct. Session is not done by I I have a MCP UI after this. So I need to cover that also. So I'm going to take these three questions and after that the rest are Rahul.
3:10:073 hours, 10 minutes, 7 secondsYeah. uh I'm having the difficulty like in this experiment the last experiment which you have shown you have shown the
3:10:143 hours, 10 minutes, 14 seconds20 tools are there okay and uh like uh those are being given to the LLM uh and
3:10:213 hours, 10 minutes, 21 secondsthat the uh the how the MCP returns like the it's a kind of the input uh this
3:10:303 hours, 10 minutes, 30 secondsinput schema right this is what we have done it in this last experiment yes okay what's the question my question this understanding this
3:10:393 hours, 10 minutes, 39 secondsexperiment what we are actually doing it that's what you describe what we did yeah thank you
3:10:463 hours, 10 minutes, 46 secondsokay okay pushka pushka
3:10:533 hours, 10 minutes, 53 secondssorry uh I was on mute uh so uh uh when we have like lot of MCP tools right so instead of like skills uh is it possible
3:11:013 hours, 11 minutes, 1 secondto use some kind of rag kind of architecture as you're over complicating skills basically But same thing.
3:11:133 hours, 11 minutes, 13 secondsSo is it possible to like store the all the density tools in some kind of DB and then query them based on query or
3:11:213 hours, 11 minutes, 21 secondsunderstanding of the Yes, you can. Okay.
3:11:303 hours, 11 minutes, 30 secondsHi Rohan. Uh so my understanding is that this uh uh MCP server and uh client we can deploy onto any other cloud or
3:11:393 hours, 11 minutes, 39 secondsanywhere right right right so say for example if I have some angular as a UI so from this I'll be
3:11:463 hours, 11 minutes, 46 secondsinvoking the uh client that will u eventually call the server or start the server correct
3:11:533 hours, 11 minutes, 53 secondsis that correct correct okay but uh so what is the handle for calling the client handle calling the client client is
3:12:023 hours, 12 minutes, 2 secondscalling something now. So how do I answer your question?
3:12:033 hours, 12 minutes, 3 secondsNo. Say for example if I'm uh if my starting like angular from that I'll have to call the client, right?
3:12:123 hours, 12 minutes, 12 secondsOkay. The question is wrong.
3:12:143 hours, 12 minutes, 14 secondsUh so uh the client client has to start the angular or in angular you have to start a service that starts a client.
3:12:223 hours, 12 minutes, 22 secondsYes, exactly. So that that's where I'm asking where how can I find the handler to call the client.
3:12:313 hours, 12 minutes, 31 secondsI'm just running here python uh agent mcp use py in your case you're going to throw a javascript command that does that
3:12:393 hours, 12 minutes, 39 secondsokay okay got it got it okay thank you uh Rohan hi Rohan I understood the session today so one thing I did not
3:12:473 hours, 12 minutes, 47 secondsunderstand is when somebody asked the question about playright so um so to to connect to the playright we have to find
3:12:553 hours, 12 minutes, 55 secondsthe MCP of playright and uh in the terminal Well, you have to do the same thing the server
3:13:043 hours, 13 minutes, 4 secondsthe play rate server py and we have to connect to the playright if you have the credentials authorization correct
3:13:123 hours, 13 minutes, 12 secondsokay but uh somebody said running it locally or something that's where I got bit confused um don't listen to them
3:13:203 hours, 13 minutes, 20 secondsoh sorry okay no further questions for next 10 minutes because I need to do this and I'm seeing people are uh leaving so
3:13:273 hours, 13 minutes, 27 secondswhere is MCP in 2627 7 a lot has changed. What I've taught you is 25 26 26 27 MCP has changed a lot now uh and
3:13:373 hours, 13 minutes, 37 secondsthis is exactly what I want you to learn because this is the future of the whole agentic uh world and you're going to see every everyone is actually doing it. Uh they're showing you graphs, they're
3:13:453 hours, 13 minutes, 45 secondsshowing you animations and uh Google is Google keeps coming out with different tools. Now we have this beautiful uh tool called prefab. Uh there might be
3:13:543 hours, 13 minutes, 54 secondsfuture competition that may come to prefab but we are going to be using prefab unless somebody better than prefab comes in. Now prefab let's see
3:14:033 hours, 14 minutes, 3 secondsread what it's saying. Prefab is a UI framework to build rich interactive interfaces in Python. Creates MCP apps data dashboards interactive tools and more than 100 plus pre-built components.
3:14:133 hours, 14 minutes, 13 secondsA bundled React render turns everything into a self-contained application.
3:14:173 hours, 14 minutes, 17 secondsComposing functions in Python and blah blah blah. Okay. So what it does is instead of MCP just returning let's say
3:14:253 hours, 14 minutes, 25 secondsURL or a Python output or uh some text or some calculation or some hyperlink or
3:14:323 hours, 14 minutes, 32 secondssome render right some text extracted it can actually throw a UI itself right so imagine MCP blender for example not just
3:14:413 hours, 14 minutes, 41 secondsresponding to change commands and all actually throwing the UI of the 3D render or imagine that Gmail is not actually only
3:14:503 hours, 14 minutes, 50 secondsGoogle calendar is not just giving you that you have a calendar events on these these days actually throws you a box where the UI is also there or imagine
3:14:583 hours, 14 minutes, 58 secondszoom actually not just telling you your zoom u you can schedule a meeting actually throws you a button where when you click actually opens the zoom there
3:15:063 hours, 15 minutes, 6 secondsitself and integration so that's where the world is going every dashboard or every application is going to be a a super app where every single other
3:15:133 hours, 15 minutes, 13 secondsfeature is going to be integrated so same app can do a zoom can do a Uber can do sugi can do GSC filing can do birth certificate can do anything I can think
3:15:223 hours, 15 minutes, 22 secondsof. So that's where the world is going and that's where the prefab comes in. So we're going to be using prefab very simple tool uh list of code is also
3:15:293 hours, 15 minutes, 29 secondsalready shared. So let's see step by step of what is happening inside. Uh first let me close all of these
3:15:383 hours, 15 minutes, 38 secondsand first open there's a lot of read me also that you can go through but here's a counter. So let me clear this and let me go inside prefab and uh python.
3:15:503 hours, 15 minutes, 50 secondsOkay, let me go further in.
3:15:583 hours, 15 minutes, 58 secondsNow here is a UI. If prefab is not there, this is how the UI will look like on a front end or or a control panel or
3:16:053 hours, 16 minutes, 5 secondsyour command prompt. If I want increment, I will press I. It will incre counter says one one. You can see the counter is increasing slowly. I can say
3:16:143 hours, 16 minutes, 14 secondsR to reset and I can say Q to quit. This is a barebone. User won't like something like this. So what can we do? Uh let's go to CD01.
3:16:263 hours, 16 minutes, 26 secondsHere we are going to be using prefab. So let's see how it's done. Very simple code. You can see nothing actually there right. So prefab ui app prefab app
3:16:353 hours, 16 minutes, 35 secondscomponent. We just rendering this prefab. So now run python
3:16:423 hours, 16 minutes, 42 secondshello py and it's going to should have opened. One second. H sorry
3:16:493 hours, 16 minutes, 49 secondsthe command is different prefab
3:16:573 hours, 16 minutes, 57 secondsserve hello py reload.
3:17:033 hours, 17 minutes, 3 secondsIt opened this page. See that?
3:17:133 hours, 17 minutes, 13 secondsSo that UI is now sent by our MCP server.
3:17:213 hours, 17 minutes, 21 secondsNow what else can we push? So let's control C. We're out.
3:17:313 hours, 17 minutes, 31 secondsSo now here we're going to be maintaining some state. Okay. So here we're going to be running
3:17:393 hours, 17 minutes, 39 secondsprefab dash reload is in case the code changes
3:17:493 hours, 17 minutes, 49 secondsat the back end. So we have a hot reload that we can look at.
3:18:003 hours, 18 minutesSo same thing but now you can see that we have a UI much better compared to what we were doing earlier right uh I can stop this
3:18:093 hours, 18 minutes, 9 secondsso let's go to CD03 so slightly more complex here we are
3:18:173 hours, 18 minutes, 17 secondsgoing to be prefab inside an MCP so we are serving this as MCP just take a look at a code it's very simple again we have a few tools and now we can use this uh
3:18:263 hours, 18 minutes, 26 secondsprefab itself as a UI itself as a tool as MC GP tool. Now we have a server py.
3:18:423 hours, 18 minutes, 42 secondsNo prefab app found. Okay.
3:18:473 hours, 18 minutes, 47 secondsUh I need to call this a tool. Okay. So I must have written the command.
3:19:183 hours, 19 minutes, 18 secondsLet's look at the inspector itself.
3:19:463 hours, 19 minutes, 46 secondsOkay.
3:19:573 hours, 19 minutes, 57 secondsOkay. So now our MCB server, the one that I just ran, is sending us two uh UI. One is for the status card and the other is for the counter card.
3:20:183 hours, 20 minutes, 18 secondsRight. So the UI itself can be now uh sent via the MTV server. Right. So let me kill
3:20:253 hours, 20 minutes, 25 secondsthis also and let's go back and show the last example.
3:20:403 hours, 20 minutes, 40 secondsNow this is the final one where we like to do slightly more than just random stuff. So here we have a prompt to app.
3:20:483 hours, 20 minutes, 48 secondsNow this is what I want you to extend in the in the example. Now this is the combination of what all we have learned today. Now here I'm going to be using Gemini 3.1. Gemini key is already there.
3:20:583 hours, 20 minutes, 58 secondsSome other stuff. This is the UI stuff that is there. And I wanted to focus on the dashboard side. The the prompt side.
3:21:083 hours, 21 minutes, 8 secondsWhere is the prompt? Yes, you design small interactive dashboards. Given the user sentence and current dashboard spec, if any, respond with a spec for the dashboard that should be shown next.
3:21:183 hours, 21 minutes, 18 secondsSo now I'm going to prompt, it's going to ask me what is it that I want. I'm going to ask Gemini to create UI for me.
3:21:243 hours, 21 minutes, 24 secondsOkay. So now
3:21:413 hours, 21 minutes, 41 secondsSo this is the UI it has sent me. I need to go back here and it is asking me what is it that I would like to do.
3:21:583 hours, 21 minutes, 58 secondsSo here I'm going to say uh make in fact I've written some good examples so I can just copy paste them.
3:22:453 hours, 22 minutes, 45 secondsLet's see what it does.
3:23:003 hours, 23 minutesIt's a very simple example and of course you can extend it you can add more u this prefab has like 200 plus components
3:23:083 hours, 23 minutes, 8 secondswe expose only few components so it is not just uh so much to handle at once and we again have at Let's see.
3:23:433 hours, 23 minutes, 43 secondsYeah, finally see that this is a UI generated.
3:23:493 hours, 23 minutes, 49 secondsSo I have portfolio tracker. This is the UI that generated. uh piano tab where it's telling me where my stocks are and
3:23:573 hours, 23 minutes, 57 secondsbased on what you want you can actually request it to make new different UIs.
3:24:013 hours, 24 minutes, 1 secondThere are other commands also that you can try. You can try add a watch list on a portfolio tab. Add a sparkle line. Uh
3:24:093 hours, 24 minutes, 9 secondsI can continue by the way. Right. So I can just take this add a watch list tab.
3:24:133 hours, 24 minutes, 13 secondsSo it will take the older one and continue it because the the prompt gets added to it. So here I'm saying add a watches tab with a table of five stocks
3:24:213 hours, 24 minutes, 21 secondsto watch. So it should if I don't get 503. And why is it getting 503? That's really weird.
3:24:313 hours, 24 minutes, 31 secondsMaybe everyone's just using it.
3:24:343 hours, 24 minutes, 34 secondsUh okay. Uh I will actually share that uh next one. I should have done earlier but I would share the Nvidia one which is much better.
3:24:563 hours, 24 minutes, 56 secondsYeah. No AP element. Okay. I'm using agent test for two. How can you say? Okay. Anyways, let's see. Yeah, it's working now.
3:25:283 hours, 25 minutes, 28 secondsOkay, let's take questions by then. Uh before I take questions, I need to go back here. Okay, we have a watch list
3:25:363 hours, 25 minutes, 36 secondstab also, right? So, you can see that you can actually ask Gemini and this is something I actually built manually uh in Arct one. Uh fortunately, we have
3:25:453 hours, 25 minutes, 45 secondsthis so I don't have to look at all the components and build it from scratch and stuff. Now, this is this will be something like MCP very soon. is already
3:25:533 hours, 25 minutes, 53 secondsMCV but I'm saying like this will be picked up by all the uh really nearly everyone so your UI can be directly
3:26:013 hours, 26 minutes, 1 secondpushed to Gemini and it will have a consistent framework now what is your assignment your assignment is write your own MCP server
3:26:083 hours, 26 minutes, 8 secondswith any three functionalities that do these things uh something related to internet it searches fetches a page gets some data API etc perform operation on
3:26:183 hours, 26 minutes, 18 secondslocal file as I did also go to Y cominator download a download the contents And I was limiting it to 2,000 characters. You need to remove that.
3:26:263 hours, 26 minutes, 26 secondsCommunicates back to you via any UI. So you need to get the UI back, right? So a prompt would be something like uh okay, use a prefab. Basically uh shows the
3:26:343 hours, 26 minutes, 34 secondsprompt that forces agent to use all three function. This is what you have to show. prompt something that uh go to
3:26:433 hours, 26 minutes, 43 secondstimesofindia.com get fetch the top 10 headline store it on a text file and then use a pre uh pre prefab UI to show
3:26:513 hours, 26 minutes, 51 secondsit show it on the uh local host or on a web view also so that's the whole sequence I wanted to do right so you need to make sure that performing the C
3:26:593 hours, 26 minutes, 59 secondstask you need to make sure that it's using prefab to demonstrate the UI uh I'm pushing you in this direction because soon you'll realize that if you
3:27:063 hours, 27 minutes, 6 secondskeep on writing UI it's not going to make sense. The UI itself will be very dynamic. You will you may arrive at a final dashboard kind of UI that my
3:27:143 hours, 27 minutes, 14 secondsdashboard will look like this but the contents inside is always going to be pushed by the LM. So show the prompt that forces the agent to use all the three uh the three things that I
3:27:223 hours, 27 minutes, 22 secondsmentioned including the prefab UI for example find the ownership details. This is example find the ownership detail of Tata Suns. Save those details in text
3:27:303 hours, 27 minutes, 30 secondsfile and show me it on a dashboard web page etc. Right? UI must be made using prefab. So that's an example prompt that I'm sharing with you. What you're
3:27:373 hours, 27 minutes, 37 secondssubmitting is a YouTube demo where I can see that uh call one, call two, call three prefab UI and you're sharing GitHub code. If you are okay to share
3:27:453 hours, 27 minutes, 45 secondsyour code with somebody else because a lot of people requested can we see the code of the best assignments also. So above code fetches 500 minimum points. U
3:27:533 hours, 27 minutes, 53 secondsmax code 2,500 depending on how beautiful you make it or how detailed you go on the prefab site and how complex your application is. Now I
3:28:013 hours, 28 minutes, 1 secondreally really wanted to push the limits of prefab and what is possible in this session itself because you'll see that NCB exposes set of tools that are
3:28:093 hours, 28 minutes, 9 secondsavailable. Prefab is going to be more such tools inside. So there's nothing special you have to do and you'll see that the UI uh that you struggling with
3:28:163 hours, 28 minutes, 16 secondsthat write react component or I don't know how to write a uh let's say Google uh Chrome uh prompt or a Google Chrome
3:28:243 hours, 28 minutes, 24 secondstoolbox uh plug-in uh make it make it beautiful. All of that is going to go out. You can just say prefab dark theme and just apply. It's going to be a very
3:28:323 hours, 28 minutes, 32 secondssimple point that is there. Okay. Now let's move to questions. K. Yeah. Hi Kish here.
3:28:393 hours, 28 minutes, 39 secondsUh the original problem statement we said that uh if we don't use MCP, right?
3:28:443 hours, 28 minutes, 44 secondsThen the context size itself will increase drastically. Correct.
3:28:483 hours, 28 minutes, 48 secondsSo like okay all the other use cases make sense but how does rendering UI uh from a MCP server makes sense right?
3:28:573 hours, 28 minutes, 57 secondsBecause anyways we are giving a prompt which is v and then in the back end my mcp server somehow we'll end up using uh
3:29:053 hours, 29 minutes, 5 secondsuh the same like some some model uh to generate the UI and give the HTML back right because at the end of
3:29:133 hours, 29 minutes, 13 secondsthe day we are rendering giving the HTML back that's what my my agent or my my client is rendering right so will it
3:29:203 hours, 29 minutes, 20 secondsreally save the tokens or the problem that MCP server uh was supposed to solve? See the question is what UI will
3:29:283 hours, 29 minutes, 28 secondsbe served and where will it serve and how how many times can you serve. You are saying that you will know precisely for each LLM output which UI needs to be served.
3:29:373 hours, 29 minutes, 37 secondsThe world is going in a direction where when you ask for example to charge GP hey can you tell me the GDP split of India it actually shows you a pie chart
3:29:433 hours, 29 minutes, 43 secondsof uh uh services agriculture manufacturing and so on. So that decision is not going to go to LM it is
3:29:523 hours, 29 minutes, 52 secondsalready going. So or for example when Uber how do you use Uber in charge GBD now for example if you don't let Uber send the UI
3:30:003 hours, 30 minutesyou saying you will write UI for every single possible use case that's not going to be possible
3:30:073 hours, 30 minutes, 7 secondsno I mean we we don't need to use the UI but I mean the the JP or my agent itself
3:30:143 hours, 30 minutes, 14 secondscan also generate some fancy HTML right that is exactly what prefab is solving now instead of forcing LM to come up
3:30:213 hours, 30 minutes, 21 secondsjust If you just go back to the prefab website and see the code required to generate that pie chart, you will be stunned how much amount of code is required here. It just is going to say
3:30:303 hours, 30 minutes, 30 secondsthat okay just push. In fact, let me show it to you. If you go on prefab
3:30:373 hours, 30 minutes, 37 secondsand if you look at uh components and if you look at
3:30:453 hours, 30 minutes, 45 secondsthat's all LM agent has to say now to generate this Okay.
3:30:553 hours, 30 minutes, 55 secondsRight. To generate something like this, just this is required in protocol and Python something like this. So,
3:31:023 hours, 31 minutes, 2 secondsso the card content we say right for example type is card content or card footer. So the card content is like must
3:31:093 hours, 31 minutes, 9 secondsbe some component uh maybe a react component or some some HTML component right which LM knows that this is the markup representation of this component.
3:31:183 hours, 31 minutes, 18 secondsI just need to fill this data which is in the children exactly what MC exactly what MCP is right this is a structure I just need to fill
3:31:263 hours, 31 minutes, 26 secondsstuff so the UI is the UI is a structured prompt structured schema and the LM just
3:31:343 hours, 31 minutes, 34 secondsputs the data in progress 99.7 button falls and so on
3:31:413 hours, 31 minutes, 41 secondsokay fair enough okay yeah can I just explain how the this flow is going on for example You
3:31:483 hours, 31 minutes, 48 secondswrote something the second example you wanted to add some uh chart. So uh you wrote some prompt and how how is the flow going on?
3:31:573 hours, 31 minutes, 57 secondsSame thing as last time. What happened last time?
3:32:003 hours, 32 minutesUh you wrote a prompt. It went to uh this Gemini. Gemini use a tool call extracted the information and I'm assume
3:32:073 hours, 32 minutes, 7 secondsthe pre prefab is also an MCP server is exposed to the Gemini model and it's calling that one and updating the UI and that's how the entire thing is going.
3:32:173 hours, 32 minutes, 17 secondsRight. Exactly. Okay. Understood. Thank you.
3:32:193 hours, 32 minutes, 19 secondsSo, same thing. So, uh same uh as we did last time. So, in the prompt we are just adding it. Okay.
3:32:263 hours, 32 minutes, 26 secondsOkay. Sep.
3:32:293 hours, 32 minutes, 29 secondsUh yeah. Uh so on this prefab is very fantastic uh thing that uh I have seen but where I'm struggling is basically
3:32:383 hours, 32 minutes, 38 secondswhat could be the possible use cases. I mean see generally what we see like MCPO right it's like a creating the mesh of
3:32:453 hours, 32 minutes, 45 secondslike all the applications and services together probably running in enterprise have you heard of perpetual lab yeah I heard
3:32:533 hours, 32 minutes, 53 secondshow will you make this UI it generates real time
3:33:013 hours, 33 minutes, 1 secondthat that is a perfect against all of this because now you can do it literally you can just take the contents send it to Gemini and ask think of this prompt.
3:33:103 hours, 33 minutes, 10 secondsOkay. Uh Gemini, I want to go online look at Indian GDP in 2627 and give me the uh areas where there's a possibility
3:33:183 hours, 33 minutes, 18 secondsof business growth given AI is going to take away so many jobs and services what what areas I should focus on and instead of just giving me a text why don't you make a dashboard for
3:33:273 hours, 33 minutes, 27 secondsyou see how moment you have this kind of question actually just generates a whole dashboard or you can say that okay why don't you make the whole website where I can just flow through the whole concept
3:33:353 hours, 33 minutes, 35 secondsand everything is linked. So now you are fully to understand.
3:33:423 hours, 33 minutes, 42 secondsIt just knows that okay I have this pie chart I have this and it just fills in content.
3:33:463 hours, 33 minutes, 46 secondsJust keep that in everyone is doing it. Charge has also started coming with some gimmicky stuff.
3:33:563 hours, 33 minutes, 56 secondsWe have plot also.
3:34:003 hours, 34 minutesSo maybe I can relate to charg where human interface right. I write something and probably chat GPT in the back end
3:34:073 hours, 34 minutes, 7 secondsexecute that prefab command for that uh prompt and pop-ups another UI where I can actually see the visual of that information.
3:34:163 hours, 34 minutes, 16 secondsYes.
3:34:173 hours, 34 minutes, 17 secondsRight. That that is what we are saying here. Right. That is what we are saying here. Okay.
3:34:223 hours, 34 minutes, 22 secondsRight. For example, periodic table. If you just ask make a periodic table for my daughter. In that case, we don't want it to create the whole UI. It's going to
3:34:293 hours, 34 minutes, 29 secondsbe humongous code. Right. Instead of just writing and providing features, we'll just spend time fixing it. Then we say, I don't like the red color, the blue color, can I make it bigger and
3:34:373 hours, 34 minutes, 37 secondssmall? All those things are gone. It can just dump this uh literally here maybe thousand tokens for all the text that's there.
3:34:463 hours, 34 minutes, 46 secondsOkay. So today, can I pass that command in the prompt itself like prefab uh I want this uh output to be coming
3:34:553 hours, 34 minutes, 55 secondsrendered as a UI. See in my code uh this is what the planner prompt is. You design small interactive dashboard given
3:35:023 hours, 35 minutes, 2 secondsthe user sentence and the current dashboard spec if any current is allowing it to look at the next command.
3:35:083 hours, 35 minutes, 8 secondsRespond with a spec for the dashboard simply be shown as you have one template dashboard. It spec is this and each tab widget is an audit list. Each widget is
3:35:173 hours, 35 minutes, 17 secondsone of the following. You have a start, you have a batch, checklist, progress, ring, pi, bar, line, spark line etc. So this is a combination of component that I have provided. If you want it to be
3:35:243 hours, 35 minutes, 24 secondsexhaustive then you need to go back to the prefab and see what all the component that are there and you can provide more set there's lambda rx there's line and other stuff right when
3:35:323 hours, 35 minutes, 32 secondsyou provide it exhaustive component it can do all of that if you go here I think it's set somewhere around 100 plus pre-built components all of these component that you're seeing it can do
3:35:403 hours, 35 minutes, 40 secondsa good example would be a page like this can you create a uh some example for me right I want to calculate the amount of
3:35:493 hours, 35 minutes, 49 secondssavings that I have depending on the interest rate depending on the uh inflation rate and so on and so on and etc. Right? So in that case when you do
3:35:563 hours, 35 minutes, 56 secondssomething like that it's not going to tell you I think based on the interested no here is the exact chart for you why don't you keep changing thing and see so
3:36:043 hours, 36 minutes, 4 secondsif you want to ask your uh chatbot or your agent to do something like this you have to have pre components ready
3:36:123 hours, 36 minutes, 12 secondsokay okay thanks yeah uh rashan
3:36:203 hours, 36 minutes, 20 secondsso can we use the same apps on set and make uh the screens dynamic. Maybe
3:36:283 hours, 36 minutes, 28 secondsexample I have an application mobile application and I have given an option to customer to customize his app screens like he may
3:36:373 hours, 36 minutes, 37 secondswant to change some button optical based on the user input. Yes.
3:36:453 hours, 36 minutes, 45 secondsYeah, that is what this is about. Okay.
3:36:503 hours, 36 minutes, 50 secondsSee this is this is claw in front of you. They are using it internally. The prefab just made it possible for us to also do it.
3:36:593 hours, 36 minutes, 59 secondsOkay.
3:37:003 hours, 37 minutesOkay. But couple of question Rhan here is what you're showing about the cloud code.
3:37:093 hours, 37 minutes, 9 secondsThis uh this rendering has been generated on the fly with the code for
3:37:163 hours, 37 minutes, 16 secondsthe web uh uh on the fly or it is like on the fly uh pre on the fly, right? on the not on the fly something like prefab
3:37:243 hours, 37 minutes, 24 secondssomething like prefab on the fly so what I understand about the prefab is what you're pointing at is it there
3:37:323 hours, 37 minutes, 32 secondswould be some metadata that has been configured in MCP with respect to component and then component will be selected by the LLM to to be rendered
3:37:403 hours, 37 minutes, 40 secondsand that that is what cloud is doing so cloud code is also following the same structure is cloudi not cloud code this is cloud
3:37:493 hours, 37 minutes, 49 secondsoh sorry cloud Right.
3:37:523 hours, 37 minutes, 52 secondsSo, uh Okay. Uh okay. My next question about the prefab is how do I customize the HTML or the content in a sense?
3:38:043 hours, 38 minutes, 4 secondsI need you need to read a prefab aspect for that. Okay. Okay.
3:38:103 hours, 38 minutes, 10 secondsSo, we can do that. But we can also be able to write our own custom component library. And of course, that that's what
3:38:193 hours, 38 minutes, 19 secondsthat's what I did. I wrote something like 200 components in octress one but I realized that managing that becomes difficult UI where the size the when I
3:38:283 hours, 38 minutes, 28 secondsreduce the screen size view on mobile there's so many different things that we have to take care of and they're maintaining it okay
3:38:373 hours, 38 minutes, 37 secondsthis is about read only data like the charts or uh content which is need to be presented if it is edit only model if
3:38:463 hours, 38 minutes, 46 secondsthere's a panel and not edit only but then editable models or panels that needs to be rendered. There would be API
3:38:533 hours, 38 minutes, 53 secondscall back end API call integration correct. So that is something will uh you have to uh you have to create
3:39:023 hours, 39 minutes, 2 secondsgenerate uh implement that way correct with your own MCD correct can I have that understanding right yes
3:39:103 hours, 39 minutes, 10 secondsfair enough thanks Kevin so um this is what u I'm understanding
3:39:193 hours, 39 minutes, 19 secondsright so MCP servers uh if it's just an uh llm u uh LLMs need to or or we need
3:39:283 hours, 39 minutes, 28 secondsto understand which tools to use um and uh we we use u LLM to um kind of get
3:39:353 hours, 39 minutes, 35 secondsthat information and then make MCP calls and then we get the data. If there's no UI required in in that scenario then prefab doesn't come into picture.
3:39:433 hours, 39 minutes, 43 secondsExactly.
3:39:443 hours, 39 minutes, 44 secondsRight. But if there are scenarios where uh let's say we get some uh tool call
3:39:503 hours, 39 minutes, 50 secondsresponse back u and if we need any UI um then what we would do is we would uh and
3:39:573 hours, 39 minutes, 57 secondsand just correct me if I'm wrong in this flow. So we make a call to that MCP server uh for that specific tool uh
3:40:043 hours, 40 minutes, 4 secondswhich LM suggested us uh we get the response back the data and then we would
3:40:103 hours, 40 minutes, 10 secondsuse pre free uh prepab uh with that data to create UI correct.
3:40:183 hours, 40 minutes, 18 secondsUh now the question is uh and then we can embed that UI in our uh in our uh uh in our app or uh something like that.
3:40:283 hours, 40 minutes, 28 secondsRight. Correct. Correct.
3:40:303 hours, 40 minutes, 30 secondsOkay. Now the question is uh is there any data privacy issue because you're sending our data to prefab and
3:40:383 hours, 40 minutes, 38 secondsno prefab is locally installed. It's a library just like react.
3:40:453 hours, 40 minutes, 45 secondsI see. Okay. Okay. So okay. So it's just a library which is uh Yes.
3:40:523 hours, 40 minutes, 52 secondsjust this a layer on top of the uh react uh correct? Uh right. Okay. This becomes easy. Okay.
3:40:593 hours, 40 minutes, 59 secondsThank you.
3:41:013 hours, 41 minutes, 1 secondHello everyone. So for my question is regarding this prefab again. So um what I understand is the LLM gives this
3:41:093 hours, 41 minutes, 9 secondsinput to the prefab um whatever um function and gets an output. So prefab is creating a UI for a snapshot of data.
3:41:203 hours, 41 minutes, 20 secondsuh it's not like a reactive uh I see like when you slide the bars and all the data changes but it already
3:41:273 hours, 41 minutes, 27 secondshas the data u coded inside that it's not a dynamic data is that right it can be dynamic can be made dynamic
3:41:353 hours, 41 minutes, 35 secondsfor example you can say that okay I make a UI that links to the stock price then a background function is running that
3:41:423 hours, 41 minutes, 42 secondskeeps updating it can be made dynamic okay and and the rendering that it's creating is that an HTML or like uh HTML
3:41:523 hours, 41 minutes, 52 secondsare we supposed to render that I mean um the HTML in whatever container we want it or what is it output
3:41:593 hours, 41 minutes, 59 secondssimple HTML HTML JavaScript simply HTML okay uh and the next question is like you have shown us the code of like how you have created a
3:42:083 hours, 42 minutes, 8 secondsprefab client to uh include that as an MCP looks like a lot of lines of code like did you like happen to type that or
3:42:163 hours, 42 minutes, 16 secondsis it like created by a uh agent again agent Again, I don't think anyone code anything at all.
3:42:223 hours, 42 minutes, 22 secondsOkay. So, you actually like asked the agent to create a client for pre prefab and like uh your requirement. Is that
3:42:303 hours, 42 minutes, 30 secondsall? Because like there's lot of custom code. It looks like there you have added prompts.
3:42:363 hours, 42 minutes, 36 secondsIt looks custom code but alternative would be that I go on a prefab website and copy the class. Right. Okay.
3:42:433 hours, 42 minutes, 43 secondsAnd uh all of this is spec code. This is not something that has any logic to it. This uh prompt is where I get involved.
3:42:513 hours, 42 minutes, 51 secondsDashboard dashboard is how I want the dashboard to look. Okay.
3:42:573 hours, 42 minutes, 57 secondsAll right. And before I like the last question is like so the prefab output is that something that we could reuse in some other component for example I have
3:43:053 hours, 43 minutes, 5 secondsapplication where UI has to be created regularly updated.
3:43:083 hours, 43 minutes, 8 secondsYes. Anywhere all these components that are there you can create anywhere. I showed you right. I was not running lm just the prefab first. Uh all right. All right. Thank you.
3:43:193 hours, 43 minutes, 19 secondsOkay.
3:43:213 hours, 43 minutes, 21 secondsUh hi. Uh R. Uh like so this specifying these components definitely better but
3:43:303 hours, 43 minutes, 30 secondsif we don't specify the components can it automatically figure it out what all the components are required to for these
3:43:373 hours, 43 minutes, 37 secondscharts and all and what all the charts are suitable for this this kind of the factual information. You're asking is the AI intelligent? Answer is yes.
3:43:483 hours, 43 minutes, 48 secondsOkay. And the second thing is that the like is the immediately the dashboard is being built and being shown. Okay. Where
3:43:573 hours, 43 minutes, 57 secondsit is hosted that dashboard local server your your computer.
3:44:033 hours, 44 minutes, 3 secondsOh okay. Thank you.
3:44:083 hours, 44 minutes, 8 secondsSo uh Rohan uh something about prefab is not clear to me. Is it like uh an output format the the way models used to do
3:44:183 hours, 44 minutes, 18 secondsmarkdown files and all what like is it is it giving an output in a particular protocol is that it
3:44:253 hours, 44 minutes, 25 secondsis exactly like that and and the prefab library is needed to just render it or what what is it just to render it
3:44:333 hours, 44 minutes, 33 secondsand and if you let's say you have 100 components available in prefab are we supposed to list the components which we are used in the prompt
3:44:413 hours, 44 minutes, 41 secondsyou have to list every single of them I listed these.
3:44:453 hours, 44 minutes, 45 secondsSo if so there is no way the model can actually search uh the best suitable component here like we have to use them here.
3:44:523 hours, 44 minutes, 52 secondsYou can use skills in session 8 910. Okay. And and how is this an MCP right?
3:45:003 hours, 45 minutesI I don't understand how is it still an MCP because this looks like just an output format which we are rendering.
3:45:073 hours, 45 minutes, 7 secondsHow is it MCP? What is MCP?
3:45:113 hours, 45 minutes, 11 secondsuh it's it's it's just a standardized way to call functions, right?
3:45:173 hours, 45 minutes, 17 secondsYes. So the prefab MCP server allows the LM to provide a standard way of calling the components.
3:45:253 hours, 45 minutes, 25 secondsSo it will give us the function name which is prefab render and argument will be the uh protocol whatever it is supposed to show.
3:45:343 hours, 45 minutes, 34 secondsCorrect. And when we run it, it converts into UI automatically.
3:45:373 hours, 45 minutes, 37 secondsOkay. And is there is there any way by which I can interact with the LLM itself from the prefab UI? Of course.
3:45:453 hours, 45 minutes, 45 secondsDoes that work? Yeah, we can.
3:45:493 hours, 45 minutes, 49 secondsOh, you can write the whole chat inside inside the prefab.
3:45:543 hours, 45 minutes, 54 secondsOkay. Uh I Yes. Okay. Say what's up.
3:46:013 hours, 46 minutes, 1 secondUh hi Rohan. So um while explaining to us you have gone to the Germany Gemini AI studio and you have given the API key
3:46:093 hours, 46 minutes, 9 secondsright I just wanted to see that step once again. What do you mean?
3:46:143 hours, 46 minutes, 14 secondsUh in the API key which API key you have uh given in the AI studio for now
3:46:213 hours, 46 minutes, 21 secondsmy API key. Uh okay your API key of prefab or uh some Gemini sorry
3:46:293 hours, 46 minutes, 29 secondsyou go to AI studio you click create API key click create whatever comes there go here you have a env file paste there and
3:46:383 hours, 46 minutes, 38 secondsuse inside okay okay for your okay okay understood for your prefab to access your AI you are giving this API key
3:46:463 hours, 46 minutes, 46 secondsvery wrong very very wrong question prefab prefab is a MCP server has nothing to do with the Gemini API
3:46:533 hours, 46 minutes, 53 secondskey. Gemini API key is for Gemini to to run this model.
3:46:593 hours, 46 minutes, 59 secondsSorry. Yes, Ro. Got it. Yeah. So, um yeah, sorry. You have used this model, right? Fine. Uh sorry. And one last question. And uh you are running the
3:47:083 hours, 47 minutes, 8 secondscommands, right? So, if I want to know the commands from the prefab website, which command is for which one or so, for example, in the command you are
3:47:153 hours, 47 minutes, 15 secondsseeing SER. So, how um how to generalize look for those commands? Ask Claude code
3:47:233 hours, 47 minutes, 23 secondsfor prefab. Uh okay. Yeah. Yeah. You'll not have to write command.
3:47:293 hours, 47 minutes, 29 secondsJust just think of what you want and let Claude or uh Gemini do it for you. It's not that difficult. Okay. Yeah.
3:47:363 hours, 47 minutes, 36 secondsIf you are interested in commands, then go on the prefab and for each of the component you will see that there's a uh
3:47:433 hours, 47 minutes, 43 secondsfor each of the component there's a command written here.
3:47:493 hours, 47 minutes, 49 secondsUnderstood. Rohan gentle as well. Got it. Thank you.
3:47:523 hours, 47 minutes, 52 secondsYeah. So someone Rohan can you go to the canvas one more time?
3:48:013 hours, 48 minutes, 1 secondGo to the first that particular the first item you have started with four items. Four items.
3:48:083 hours, 48 minutes, 8 secondsUh yeah. Send an email. Schedule a meeting with your team.
3:48:163 hours, 48 minutes, 16 secondsWait. So wait wait wait. You just crossed it. Yes. This is the four items, right? So let's say there is a fifth
3:48:223 hours, 48 minutes, 22 secondsitem where I need I want uh that a confirmation as well as a beautiful UI
3:48:303 hours, 48 minutes, 30 secondsuh stating that everything is done for you. You can go and sleep. What's the question?
3:48:363 hours, 48 minutes, 36 secondsOkay. So the question is if I need to uh add these five task over there and I
3:48:433 hours, 48 minutes, 43 secondsneed that prefab to be the final one which can show me the UI. Now the question is is that something uh I'm
3:48:533 hours, 48 minutes, 53 secondsjust confused that after four what I need to do so that it can go for prefab and give me an beautiful UI
3:49:013 hours, 49 minutes, 1 secondjust say the use prefab for for generating beautiful UI and okay one more question if you go to
3:49:103 hours, 49 minutes, 10 secondsthe code all together uh again yes here you have direct you have uh have this thing where you are
3:49:183 hours, 49 minutes, 18 secondswhere you are having this output schema and what is the rendering type and all together right so instead of that if I just give a prompt that hey I need this
3:49:273 hours, 49 minutes, 27 secondsto be an prefab UI compatible give me the code and display it in a UI will that will that
3:49:353 hours, 49 minutes, 35 secondshelp or will that suffice my task or do I need to provide all these whatever items you have given so if you say go to prefab figure out
3:49:433 hours, 49 minutes, 43 secondshow to do it then you need to provide it access to internet access to install stuff access to do some more stuff and then it can do it for you
3:49:513 hours, 49 minutes, 51 secondsor otherwise I need to install prefab previously I mean the way you have installed in it correct Python then asking to do that
3:50:003 hours, 50 minutescorrect all right thank you okay yeah uh so as far as I see like uh
3:50:103 hours, 50 minutes, 10 secondsprefab is generating very basic HTML and all so if you want to develop something complex uh highly efficient websites if
3:50:173 hours, 50 minutes, 17 secondsyou if you want to use ReactJS is there any extension like prefab for doing the react generating the ReactJS and all or
3:50:253 hours, 50 minutes, 25 secondswe have to give it in the prompt like giving whatever required and generate this one into the uh ReactJS and give the code is something like that we have
3:50:333 hours, 50 minutes, 33 secondsto do with the LM prefab is to use already generated components they have 100 plus components if you think your component is not there
3:50:403 hours, 50 minutes, 40 secondsthen you'll have to write it uh okay got it okay a
3:50:483 hours, 50 minutes, 48 secondsUh so uh like last time you'll be sharing this code also.
3:50:563 hours, 50 minutes, 56 secondsYes sir, it is there already.
3:50:583 hours, 50 minutes, 58 secondsOkay. And Ron this session recording uh can you download for our reference future or when how much time it will be
3:51:063 hours, 51 minutes, 6 secondsavailable? It is available for live. Okay. Okay. Thank you. That's okay.
3:51:133 hours, 51 minutes, 13 secondsThank you. Okay. Bye.
3:51:233 hours, 51 minutes, 23 secondsYeah. So, um simply the prehab is a uh you know I can use it when I want to see
3:51:323 hours, 51 minutes, 32 secondsmy you know agent when I want to see the output of my question you know which is you know seen by agent uh in the UI I
3:51:403 hours, 51 minutes, 40 secondscan use this you know prefer right correct.
3:51:433 hours, 51 minutes, 43 secondsOkay. And you know this this is hosted in the local local server means local machine means it is in the sandbox. Correct.
3:51:513 hours, 51 minutes, 51 secondsIt is no that doesn't mean it is in the sandbox. You have to put it in the sandbox. But prefab doesn't need to be in sandbox because it's not uh running any code on your local machine.
3:52:023 hours, 52 minutes, 2 secondsUnderstood. Thank you.
3:52:043 hours, 52 minutes, 4 secondsOkay. Kevin supan so prefab is is prefab itself running in
3:52:113 hours, 52 minutes, 11 secondsHTTP server how is it running it is running itself in server what what is running it is running it own server
3:52:203 hours, 52 minutes, 20 secondsbut but what if you are uh what if in the case where you are embedding these in the chat itself then in that case how does it work
3:52:273 hours, 52 minutes, 27 secondsit's throwing a component that we can render it throws a component component that we can render And there prefab is not running in HTTP server separately.
3:52:373 hours, 52 minutes, 37 secondsYes.
3:52:393 hours, 52 minutes, 39 secondsAnd uh okay. Um so so in so suppose we are building a chrome plug-in where this
3:52:473 hours, 52 minutes, 47 secondsprefab is supposed to be used as a response.
3:52:503 hours, 52 minutes, 50 secondsSo there is no Python code running anywhere in that is that right?
3:52:553 hours, 52 minutes, 55 secondsWe can run it without Python if that is what you're asking. Yes, we can run it without a Python code. Right. Correct. Okay. Thanks.
3:53:023 hours, 53 minutes, 2 secondsOkay Kevin.
3:53:043 hours, 53 minutes, 4 secondsUm so if you go back to the uh free uh app uh so here uh yeah once we make the
3:53:113 hours, 53 minutes, 11 secondsuh llm call llm call decides on uh one of the components uh and the response
3:53:193 hours, 53 minutes, 19 secondswould be uh that component like what component and then we make a call to free uh free uh mcp server uh with that
3:53:273 hours, 53 minutes, 27 secondscomponent uh and what's the return uh information this is from that return information.
3:53:353 hours, 53 minutes, 35 secondsNo, this is from the LM, right? Yeah.
3:53:383 hours, 53 minutes, 38 secondsOkay. Now, after LM returns us this information, uh we make uh MCP call uh to FPAP. That's correct.
3:53:463 hours, 53 minutes, 46 secondsOkay. And then what would be that return information from the HTML the the the whole HTML the component?
3:53:583 hours, 53 minutes, 58 secondsYeah. Uh, so it would be an HTML component
3:54:053 hours, 54 minutes, 5 secondsuh which we would then uh that is render the moment there's a a component sent to prefab that gets
3:54:123 hours, 54 minutes, 12 secondsrendered on the uh local local website this app.
3:54:213 hours, 54 minutes, 21 secondsOkay. And this would be our app um this is going to be your app.
3:54:263 hours, 54 minutes, 26 secondsOkay. and and and the HTML would it be like an uh HTML or
3:54:333 hours, 54 minutes, 33 secondswould it be a a free uh component? Then we would need to prefab component.
3:54:393 hours, 54 minutes, 39 secondsOkay. So we will have to uh uh in our app we will have to install the prefab library so that it can those components.
3:54:483 hours, 54 minutes, 48 secondsCorrect. So yeah the CSS and other things are there. Got it. Okay. So thank you. Okay.
3:54:553 hours, 54 minutes, 55 secondsRohan this is not related to prefab but uh in in uh in in this current assignment you have said there is a tool which we need to create where uh which
3:55:033 hours, 55 minutes, 3 secondscan fetch something from internet. So in the assignment which I submitted this week I had created a tool like that but in many cases it will just give 4034 bit
3:55:123 hours, 55 minutes, 12 secondsand even though that website is accessible without login uh like and
3:55:193 hours, 55 minutes, 19 secondsthen cl was also not able to solve it properly for me like is it like common I mean I don't know what you're saying
3:55:283 hours, 55 minutes, 28 secondsso it will just give some uh I I think these websites are defending themselves from bots and crawlers and stuff is why
3:55:353 hours, 55 minutes, 35 secondsit was happening but uh have you faced or is there a way around this?
3:55:403 hours, 55 minutes, 40 secondsThere there's a way around but we are some six sessions away from it.
3:55:453 hours, 55 minutes, 45 secondsOh, you have to fake a browser proper browser. Okay. Okay.
3:55:523 hours, 55 minutes, 52 secondsYeah. Rohan. So this prefab uh skill you have to give to the formatter agent in the in in our harness or it will be separate agent. How would you plug it in?
3:56:003 hours, 56 minutesUh today it's same but in future it's going to be a separate agent. You can already see right I have so much of this stuff. I'm pushing you to realize that
3:56:083 hours, 56 minutes, 8 secondsthat okay I have this also then I have MCB20 tools also the context is going to be big. You're going to see getting confused. You'll see I was also struggling locally right. It just
3:56:163 hours, 56 minutes, 16 secondscouldn't look at the Y combinator simple page and do it.
3:56:213 hours, 56 minutes, 21 secondsSo future we'll have multiple agent that so I'm pushing everyone to understand that why do we need multiple agents because all of you are coming going to read online. I have 1 million context
3:56:303 hours, 56 minutes, 30 secondsopus can handle everything. So why do I need multiple agents? So I'm going to push you till the edge where you come back and say no it's not working out.
3:56:373 hours, 56 minutes, 37 secondsOkay. So so I would add a new UI agent kind of stuff.
3:56:413 hours, 56 minutes, 41 secondsYou'll have a new sub agent that will spawn it will do its work and you will kill it.
3:56:463 hours, 56 minutes, 46 secondsOkay. Okay. And that will eclipse the uh format agent uh that we had in orchestrator earlier or I mean because
3:56:523 hours, 56 minutes, 52 secondsthat just generates some markdown or or some some report right in some format. Correct. Okay. Thanks. Okay.
3:57:013 hours, 57 minutes, 1 seconduh hey Rohan uh so let's say I connect with a MCP uh uh server and uh one time I've
3:57:083 hours, 57 minutes, 8 secondsconnected I want to so MCP servers are mainly used for one time calls like they would uh incur LM costs every time if I
3:57:163 hours, 57 minutes, 16 secondswere to call them std IO is one time SSE or streaming is continuous
3:57:253 hours, 57 minutes, 25 secondsno so if it's if it's my hosted MCP server But uh if let's say I am connecting with any external party then every MCP server
3:57:343 hours, 57 minutes, 34 secondscall would host me some uh cost me some charges right because it will be an agent which is calling it
3:57:413 hours, 57 minutes, 41 secondsno if I call uh Gmail server Gmail API I don't get charged beyond the limit of course
3:57:493 hours, 57 minutes, 49 secondsLM will be charged LM LM will be charged will be charged right so what I'm seeing is uh once if I have
3:57:563 hours, 57 minutes, 56 secondsconnected with a MCP server And I know that this is going to be a uh like repeated call for me. Uh can I do a
3:58:043 hours, 58 minutes, 4 secondsconversion of that MCP call into a API call on my side and just put it in code?
3:58:103 hours, 58 minutes, 10 secondsYou're going back to 2020 the exact thing MCP wanted to solve. The moment you convert into API then you have to tell your LM that this is how you call
3:58:173 hours, 58 minutes, 17 secondsit. So it will have to remember that API call and API calls to Zoom to Yahoo to Google to Microsoft to OpenAI to Gemini
3:58:263 hours, 58 minutes, 26 secondsto Zoho to Slack to Telegram everything is different again unsolving the problem MCP solved.
3:58:343 hours, 58 minutes, 34 secondsNo no what I'm exactly trying to ask is let's say I have to integrate with some vendor which is a regular call for my platform. Okay. Answer this answer this question.
3:58:423 hours, 58 minutes, 42 secondsDo you need a LM to to talk to the vendor? M not really.
3:58:483 hours, 58 minutes, 48 secondsSo that's the answer. You can continue the connection as long as you want. Okay.
3:58:543 hours, 58 minutes, 54 secondsAnd you can continue call using API or MCP. Completely your call. The future is MCP.
3:59:033 hours, 59 minutes, 3 secondsOkay.
3:59:053 hours, 59 minutes, 5 secondsYou you you saw in the second in the third session, right? We were calling MCP manually. So you can call MCP manually. You don't need LM to call it.
3:59:133 hours, 59 minutes, 13 secondsGot it.
3:59:143 hours, 59 minutes, 14 secondsThat will change. So instead of calling the API, you'll call it through MCP. So all your calls also going to be same. Mhm. Okay. Yeah.
3:59:223 hours, 59 minutes, 22 secondsOkay. Pushcolan, I was actually thinking of some app that would compare the price of some uh item
3:59:313 hours, 59 minutes, 31 secondssay for iPhone 15 in some various sites like Amazon, Flip Cut uh and Chroma. And uh when I was trying to do this without
3:59:393 hours, 59 minutes, 39 secondsany uh API call so it was trying to just uh uh scrape the data from the websites
3:59:463 hours, 59 minutes, 46 secondsbut it was not accurate. So in order to accomplish this do I have to actually get the APIs from various uh providers
3:59:543 hours, 59 minutes, 54 secondsand write a sort of uh MC MCB server for each of them.
3:59:593 hours, 59 minutes, 59 secondsYou're doing at a scale or once in a while? Uh I was just thinking of some uh API.
4:00:064 hours, 6 secondsIt's not any sorry it's a sample project I was thinking of just wants to understand what is the approach should I take
4:00:134 hours, 13 secondsyou don't need a proper API for that but we we need a proper browser on our end to uh tell Amazon that we are not agent
4:00:214 hours, 21 secondsso we seven sessions away from that okay okay thank you okay Kevin
4:00:284 hours, 28 secondsso uh prefab is they are they hosting their own MCP no they're providing the MCP you can download it.
4:00:374 hours, 37 secondsOkay.

