
    const knowledgeBase = [
        {
            intent: 'salam',
            keywords: ['salam', 'assalamu', 'assalamualaikum', 'আসসালামু', 'সালাম', 'slm', 'asw'],
            response: "ওয়ালাইকুম আসসালাম! স্বাগতম। আমি আপনাকে কিভাবে সাহায্য করতে পারি? 😊"
        },
        {
            intent: 'hello',
            keywords: ['hello', 'hi', 'hey', 'start', 'shuru', 'হাই', 'হ্যালো', 'হেই', 'শুরু'],
            response: "হ্যালো! স্বাগতম Osmani Khelafot Support এ। আমি আপনাকে কিভাবে সাহায্য করতে পারি? 👋"
        },
        {
            intent: 'how_are_you',
            keywords: ['kemon', 'kmn', 'khobor', 'obostha', 'keamon', 'কেমন', 'খবর', 'ভালো আছেন'],
            response: "আলহামদুলিল্লাহ, আমি ভালো আছি! আপনি কেমন আছেন? কোনো সাহায্য লাগবে? 🤖"
        },
        {
            intent: 'schedule',
            keywords: ['somoy', 'kokhon', 'kbe', 'kobe', 'time', 'schedule', 'release', 'date', 'ep', 'episode', 'সময়', 'কখন', 'রিলিজ', 'তারিখ', 'পর্ব', 'কবে'],
            response: `📌 <b>সিরিজের সময়সূচী (বাংলা সাবটাইটেল):</b><br><br>
            1️⃣ <b>মেহমেদ ফেতিহলার সুলতানি:</b> প্রতি বুধবার সকাল ৬-৭ টায়।<br>
            2️⃣ <b>কুরুলুস উরহান:</b> প্রতি বৃহস্পতিবার সকাল ৫-৬ টায়।<br><br>
            <i>(টেকনিক্যাল কারণে মাঝে মাঝে ১ ঘন্টা দেরি হতে পারে)</i>`
        },
        {
            intent: 'premium',
            keywords: ['premium', 'buy', 'taka', 'cost', 'dam', 'subscription', 'bkash', 'payment', 'access', 'প্রিমিয়াম', 'টাকা', 'দাম', 'কেনা', 'সাবস্ক্রিপশন', 'পেমেন্ট', 'বিকাশ'],
            response: `💎 <b>প্রিমিয়াম মেম্বারশিপ:</b><br><br>
            আমাদের প্রিমিয়াম সাইটে অ্যাড-ফ্রি এবং ফাস্ট সার্ভারে সিরিজ দেখতে সাবস্ক্রিপশন নিন।<br><br>
            👉 <b>সাবস্ক্রাইব করতে:</b> <a href="https://osmanikhelafot.com/bkash" target="_blank" class="bot-link">osmanikhelafot.com/bkash</a><br><br>
            কোনো সমস্যা হলে এডমিনের সাথে কথা বলুন।`
        },
        {
            intent: 'admin',
            keywords: ['admin', 'help', 'contact', 'owner', 'malik', 'problem', 'msg', 'message', 'support', 'এডমিন', 'মালিক', 'সাহায্য', 'সমস্যা', 'যোগাযোগ', 'কথা'],
            response: `📞 <b>এডমিনদের কন্টাক্ট ইনফো:</b><br><br>
            সমস্যা সমাধানের জন্য টেলিগ্রামে মেসেজ দিন:<br>
            👤 <a href="https://t.me/lalinhossain" target="_blank" class="bot-link">@lalinhossain</a><br>
            👤 <a href="https://t.me/arif98101" target="_blank" class="bot-link">@arif98101</a><br>
            👤 <a href="https://t.me/no_one_76" target="_blank" class="bot-link">@no_one_76</a><br>
            👤 <a href="https://t.me/Asifjoarder2" target="_blank" class="bot-link">@Asifjoarder2</a><br><br>
            <i>⚠️ দয়া করে সালাম দিয়ে মূল সমস্যাটি এক মেসেজে লিখুন।</i>`
        },
        {
            intent: 'links',
            keywords: ['link', 'website', 'site', 'page', 'fb', 'facebook', 'group', 'telegram', 'channel', 'লিংক', 'ওয়েবসাইট', 'সাইট', 'পেজ', 'গ্রুপ', 'টেলিগ্রাম'],
            response: `🌐 <b>প্রয়োজনীয় লিংকসমূহ:</b><br><br>
            🔹 <b>ফ্রি সাইট:</b> <a href="http://www.osmanikhelafot.net" target="_blank" class="bot-link">osmanikhelafot.net</a><br>
            🔸 <b>প্রিমিয়াম সাইট:</b> <a href="https://premium.osmanikhelafot.com" target="_blank" class="bot-link">premium.osmanikhelafot.com</a><br>
            ✈️ <b>টেলিগ্রাম চ্যানেল:</b> <a href="https://t.me/OsmaniKhelafott" target="_blank" class="bot-link">Join Channel</a>`
        },
        {
            intent: 'thanks',
            keywords: ['thanks', 'dhonnobad', 'thank', 'valo', 'good', 'ok', 'thik', 'ধন্যবাদ', 'থ্যাংকস', 'ভালো', 'ঠিক'],
            response: "আপনাকেও ধন্যবাদ! আমাদের সাথে থাকার জন্য কৃতজ্ঞ। ❤️"
        },
        {
            intent: 'identity',
            keywords: ['who', 'you', 'name', 'tumi', 'ke', ' परिचय', 'তুমি', 'কে', 'নাম', 'কি'],
            response: "আমি উসমানী খেলাফতের একজন ভার্চুয়াল অ্যাসিস্ট্যান্ট। আমি অটোমেটিক উত্তর দিয়ে আপনাকে সাহায্য করার চেষ্টা করছি। 🤖"
        }
    ];

    const fallbackResponse = "আমি দুঃখিত, আমি ঠিক বুঝতে পারিনি। 🤔<br>আপনি কি <b>সিরিজের সময়</b>, <b>প্রিমিয়াম</b> বা <b>এডমিন কন্টাক্ট</b> সম্পর্কে জানতে চান? দয়া করে একটু স্পষ্ট করে লিখুন।";

    const chatWindow = document.getElementById('chatWindow');
    const chatBody = document.getElementById('chatBody');
    const userInput = document.getElementById('userInput');
    const typingIndicator = document.getElementById('typingIndicator');

    function toggleChat() {
        chatWindow.classList.toggle('hidden');
        if (!chatWindow.classList.contains('hidden')) {
            chatBody.scrollTop = chatBody.scrollHeight;
            userInput.focus();
        }
    }

    function addMessage(text, sender) {
        const div = document.createElement('div');
        div.className = `flex items-start gap-2 animate-fade-in ${sender === 'user' ? 'flex-row-reverse' : ''}`;
        
        let avatar = sender === 'bot' 
            ? `<div class="w-8 h-8 rounded-full bg-white border border-gray-200 flex-shrink-0 flex items-center justify-center shadow-sm"><i class="fas fa-robot text-yellow-600 text-xs"></i></div>` 
            : `<div class="w-8 h-8 rounded-full bg-yellow-600 flex-shrink-0 flex items-center justify-center text-white"><i class="fas fa-user text-xs"></i></div>`;
        
        let bubbleClass = sender === 'bot' ? 'chat-bubble-bot' : 'chat-bubble-user';
        
        div.innerHTML = `${avatar}<div class="${bubbleClass} p-3 text-sm max-w-[80%] leading-relaxed font-hind">${text}</div>`;
        
        chatBody.appendChild(div);
        chatBody.scrollTop = chatBody.scrollHeight;
    }

    function handleQuickAction(intent) {
        let msg = "";
        if(intent === 'schedule') msg = "সিরিজের সময়সূচী";
        if(intent === 'links') msg = "সব লিংক";
        if(intent === 'admin') msg = "এডমিন কন্টাক্ট";
        if(intent === 'premium') msg = "প্রিমিয়াম মেম্বারশিপ";
        
        handleUserSubmit(null, msg);
    }

    async function handleUserSubmit(e, text = null) {
        if (e) e.preventDefault();
        
        const rawInput = text || userInput.value.trim();
        if (!rawInput) return;

        addMessage(rawInput, 'user');
        userInput.value = '';
        
        typingIndicator.classList.remove('hidden');
        chatBody.scrollTop = chatBody.scrollHeight;

        setTimeout(() => {
            typingIndicator.classList.add('hidden');
            const response = generateAIResponse(rawInput);
            addMessage(response, 'bot');
        }, 600 + Math.random() * 400); 
    }

    function generateAIResponse(input) {
        const cleanInput = input.toLowerCase().replace(/[^\w\s\u0980-\u09FF]/gi, '');
        const inputTokens = cleanInput.split(/\s+/);

        let bestMatch = null;
        let highestScore = 0;

        knowledgeBase.forEach(category => {
            let score = 0;
            category.keywords.forEach(keyword => {
                const cleanKeyword = keyword.toLowerCase();
                if (inputTokens.includes(cleanKeyword)) {
                    score += 10;
                } 
                else if (cleanInput.includes(cleanKeyword)) {
                    score += 3;
                }
            });

            if (score > highestScore) {
                highestScore = score;
                bestMatch = category;
            }
        });

        if (bestMatch && highestScore >= 3) {
            return bestMatch.response;
        }

        return fallbackResponse;
    }
