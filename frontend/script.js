// ============================================================
// CIVICAI FRONTEND
// ============================================================

const API_BASE = "http://127.0.0.1:8000";


// ============================================================
// DOM
// ============================================================

const sections = {
    home: document.getElementById("home-section"),
    assistant: document.getElementById("assistant-section"),
    finder: document.getElementById("finder-section")
};

const navLinks = document.querySelectorAll(".nav-link");

const chatMessages =
    document.getElementById("chatMessages");

const chatForm =
    document.getElementById("chatForm");

const chatInput =
    document.getElementById("chatInput");

const sendButton =
    document.getElementById("sendButton");

const finderForm =
    document.getElementById("finderForm");

const finderResults =
    document.getElementById("finderResults");

const schemeResultsGrid =
    document.getElementById("schemeResultsGrid");

const toast =
    document.getElementById("toast");

const toastMessage =
    document.getElementById("toastMessage");

const toastIcon =
    document.getElementById("toastIcon");


// ============================================================
// NAVIGATION
// ============================================================

function showSection(sectionName) {

    Object.values(sections).forEach(
        section => {
            section.classList.remove(
                "active-section"
            );
        }
    );


    if (sections[sectionName]) {

        sections[sectionName]
            .classList.add(
                "active-section"
            );
    }


    navLinks.forEach(link => {

        link.classList.toggle(
            "active",
            link.dataset.section === sectionName
        );

    });


    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
}


document
    .querySelectorAll("[data-section]")
    .forEach(element => {

        element.addEventListener(
            "click",
            () => {

                showSection(
                    element.dataset.section
                );

            }
        );

    });


document
    .getElementById("brandButton")
    .addEventListener(
        "click",
        () => showSection("home")
    );


document
    .getElementById("heroChatButton")
    .addEventListener(
        "click",
        () => {

            showSection("assistant");

            setTimeout(
                () => chatInput.focus(),
                300
            );

        }
    );


document
    .getElementById("heroFinderButton")
    .addEventListener(
        "click",
        () => showSection("finder")
    );


document
    .getElementById("sidebarFinderButton")
    .addEventListener(
        "click",
        () => showSection("finder")
    );


// ============================================================
// TOAST
// ============================================================

let toastTimer;


function showToast(
    message,
    type = "success"
) {

    toastMessage.textContent =
        message;


    toastIcon.textContent =
        type === "error"
            ? "!"
            : "✓";


    toast.classList.add(
        "show"
    );


    clearTimeout(
        toastTimer
    );


    toastTimer =
        setTimeout(
            () => {

                toast.classList.remove(
                    "show"
                );

            },
            3000
        );
}


// ============================================================
// CHAT
// ============================================================

function removeWelcomeMessage() {

    const welcome =
        document.querySelector(
            ".welcome-message"
        );

    if (welcome) {
        welcome.remove();
    }
}


function addUserMessage(message) {

    removeWelcomeMessage();


    const wrapper =
        document.createElement(
            "div"
        );

    wrapper.className =
        "message user";


    wrapper.innerHTML = `
        <div class="message-content">
            ${escapeHtml(message)}
        </div>

        <div class="message-avatar">
            You
        </div>
    `;


    chatMessages.appendChild(
        wrapper
    );


    scrollChatToBottom();
}


function addTypingMessage() {

    const wrapper =
        document.createElement(
            "div"
        );

    wrapper.className =
        "message";

    wrapper.id =
        "typingMessage";


    wrapper.innerHTML = `
        <div class="message-avatar">
            ✦
        </div>

        <div class="message-content">
            <div class="typing">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;


    chatMessages.appendChild(
        wrapper
    );


    scrollChatToBottom();
}


function removeTypingMessage() {

    const typing =
        document.getElementById(
            "typingMessage"
        );

    if (typing) {
        typing.remove();
    }
}


function formatAnswer(text) {

    let safe =
        escapeHtml(text);


    // Bold markdown
    safe = safe.replace(
        /\*\*(.*?)\*\*/g,
        "<strong>$1</strong>"
    );


    // Numbered lists
    safe = safe.replace(
        /(^|\n)(\d+)\.\s+(.*)/g,
        "$1<div class=\"answer-list-item\"><strong>$2.</strong> $3</div>"
    );


    // Bullet lists
    safe = safe.replace(
        /(^|\n)[-*]\s+(.*)/g,
        "$1<div class=\"answer-list-item\">• $2</div>"
    );


    // Line breaks
    safe = safe.replace(
        /\n/g,
        "<br>"
    );


    return safe;
}


function addAssistantMessage(
    answer,
    sources = []
) {

    const wrapper =
        document.createElement(
            "div"
        );

    wrapper.className =
        "message";


    let sourceHTML = "";


    if (
        sources &&
        sources.length > 0
    ) {

        sourceHTML = `
            <div class="source-box">

                <div class="source-label">
                    ✓ Government source
                </div>

                ${sources
                    .map(source => `
                        <a
                            class="source-link"
                            href="${escapeAttribute(source.url)}"
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            ${escapeHtml(source.title)}
                        </a>
                    `)
                    .join("")
                }

            </div>
        `;
    }


    wrapper.innerHTML = `
        <div class="message-avatar">
            ✦
        </div>

        <div class="message-content">

            <div>
                ${formatAnswer(answer)}
            </div>

            ${sourceHTML}

        </div>
    `;


    chatMessages.appendChild(
        wrapper
    );


    scrollChatToBottom();
}


function scrollChatToBottom() {

    chatMessages.scrollTo({
        top:
            chatMessages.scrollHeight,
        behavior: "smooth"
    });
}


async function sendChatMessage(
    message
) {

    const cleanMessage =
        message.trim();


    if (!cleanMessage) {

        showToast(
            "Please enter a question.",
            "error"
        );

        return;
    }


    addUserMessage(
        cleanMessage
    );


    chatInput.value = "";

    autoResizeTextarea();


    sendButton.disabled = true;


    addTypingMessage();


    try {

        const response =
            await fetch(
                `${API_BASE}/chat`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        message:
                            cleanMessage
                    })
                }
            );


        if (!response.ok) {

            throw new Error(
                `Server returned ${response.status}`
            );
        }


        const data =
            await response.json();


        removeTypingMessage();


        addAssistantMessage(
            data.answer ||
                "I couldn't generate an answer.",
            data.sources || []
        );


    } catch (error) {

        console.error(
            "Chat error:",
            error
        );


        removeTypingMessage();


        addAssistantMessage(
            "I couldn't connect to CivicAI right now. Please make sure the FastAPI backend and Ollama are running."
        );


        showToast(
            "Could not connect to backend.",
            "error"
        );

    } finally {

        sendButton.disabled = false;

        chatInput.focus();
    }
}


// ============================================================
// CHAT FORM
// ============================================================

chatForm.addEventListener(
    "submit",
    event => {

        event.preventDefault();

        sendChatMessage(
            chatInput.value
        );

    }
);


// ============================================================
// ENTER TO SEND
// ============================================================

chatInput.addEventListener(
    "keydown",
    event => {

        if (
            event.key === "Enter"
            && !event.shiftKey
        ) {

            event.preventDefault();

            chatForm.requestSubmit();
        }

    }
);


// ============================================================
// TEXTAREA AUTO RESIZE
// ============================================================

function autoResizeTextarea() {

    chatInput.style.height =
        "auto";


    chatInput.style.height =
        Math.min(
            chatInput.scrollHeight,
            120
        ) + "px";
}


chatInput.addEventListener(
    "input",
    autoResizeTextarea
);


// ============================================================
// SUGGESTIONS
// ============================================================

document
    .querySelectorAll(
        "[data-question]"
    )
    .forEach(button => {

        button.addEventListener(
            "click",
            () => {

                const question =
                    button.dataset.question;


                showSection(
                    "assistant"
                );


                setTimeout(
                    () => {

                        sendChatMessage(
                            question
                        );

                    },
                    250
                );

            }
        );

    });


// ============================================================
// CLEAR CHAT
// ============================================================

document
    .getElementById(
        "clearChatButton"
    )
    .addEventListener(
        "click",
        () => {

            chatMessages.innerHTML = `
                <div class="welcome-message">

                    <div class="welcome-icon">
                        ✦
                    </div>

                    <h2>
                        How can I help?
                    </h2>

                    <p>
                        Ask me about the government information
                        available in the CivicAI knowledge base.
                    </p>

                    <div class="welcome-examples">

                        <button
                            data-question="What are the eligibility requirements for the scholarship?"
                        >
                            What are the scholarship requirements?
                        </button>

                        <button
                            data-question="What is the scholarship about?"
                        >
                            What is this scholarship?
                        </button>

                    </div>

                </div>
            `;


            attachWelcomeButtons();


            showToast(
                "Conversation cleared."
            );

        }
    );


// ============================================================
// FINDER
// ============================================================

finderForm.addEventListener(
    "submit",
    async event => {

        event.preventDefault();


        const ageValue =
            document.getElementById(
                "age"
            ).value;


        const incomeValue =
            document.getElementById(
                "income"
            ).value;


        const education =
            document.getElementById(
                "education"
            ).value;


        const occupation =
            document.getElementById(
                "occupation"
            ).value;


        const state =
            document.getElementById(
                "state"
            ).value;


        const selectedCategory =
            document.querySelector(
                'input[name="category"]:checked'
            );


        const submitButton =
            document.getElementById(
                "finderSubmit"
            );


        const profile = {

            age:
                ageValue
                    ? Number(ageValue)
                    : null,

            education:
                education || null,

            state:
                state || null,

            occupation:
                occupation || null,

            annual_income:
                incomeValue
                    ? Number(incomeValue)
                    : null,

            category:
                selectedCategory
                    ? selectedCategory.value
                    : null

        };


        if (
            !profile.age &&
            !profile.education &&
            !profile.annual_income &&
            !profile.occupation &&
            !profile.category
        ) {

            showToast(
                "Tell us at least one thing about yourself.",
                "error"
            );

            return;
        }


        submitButton.disabled =
            true;


        submitButton.innerHTML = `
            <span>Finding matches...</span>
            <span>•••</span>
        `;


        try {

            const response =
                await fetch(
                    `${API_BASE}/find-schemes`,
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify(
                                profile
                            )
                    }
                );


            if (!response.ok) {

                throw new Error(
                    `Server returned ${response.status}`
                );
            }


            const data =
                await response.json();


            renderSchemeResults(
                data.results || []
            );


            finderResults.classList.remove(
                "hidden"
            );


            finderResults.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });


        } catch (error) {

            console.error(
                "Finder error:",
                error
            );


            showToast(
                "Could not connect to CivicAI.",
                "error"
            );

        } finally {

            submitButton.disabled =
                false;


            submitButton.innerHTML = `
                <span>Find matching schemes</span>
                <span>→</span>
            `;

        }

    }
);


// ============================================================
// RENDER SCHEME RESULTS
// ============================================================

function renderSchemeResults(
    results
) {

    schemeResultsGrid.innerHTML = "";


    if (!results.length) {

        schemeResultsGrid.innerHTML = `

            <div class="scheme-card">

                <div class="scheme-category">
                    No strong matches found
                </div>

                <h3>
                    CivicAI couldn't find a matching
                    scheme in the current knowledge base.
                </h3>

                <p class="scheme-objective">
                    This does not mean that no government
                    scheme exists for you. It only means
                    that CivicAI does not currently have
                    enough relevant information to identify
                    one safely.
                </p>

            </div>

        `;

        return;
    }


    results.forEach(
        scheme => {

            const card =
                document.createElement(
                    "article"
                );

            card.className =
                "scheme-card";


            const reasons =
                scheme.reasons || [];


            const warnings =
                scheme.warnings || [];


            card.innerHTML = `

                <div class="scheme-card-header">

                    <div>

                        <div class="scheme-category">
                            ${escapeHtml(
                                scheme.category ||
                                "Government Scheme"
                            )}
                        </div>

                        <h3>
                            ${escapeHtml(
                                scheme.short_name ||
                                scheme.name ||
                                "Government Scheme"
                            )}
                        </h3>

                    </div>


                    <div class="match-score">

                        <strong>
                            ${Number(
                                scheme.match_percentage || 0
                            )}%
                        </strong>

                        <span>
                            MATCH
                        </span>

                    </div>

                </div>


                <p class="scheme-objective">

                    ${escapeHtml(
                        scheme.objective ||
                        "Government assistance information available in the CivicAI knowledge base."
                    )}

                </p>


                ${
                    reasons.length
                    ? `
                        <div class="match-reasons">

                            <div class="match-reasons-title">
                                Why it appeared
                            </div>

                            <ul>

                                ${reasons
                                    .map(
                                        reason =>
                                            `<li>${escapeHtml(reason)}</li>`
                                    )
                                    .join("")
                                }

                            </ul>

                        </div>
                    `
                    : ""
                }


                ${
                    warnings.length
                    ? `
                        <div class="scheme-warning">
                            ⚠ ${escapeHtml(
                                warnings.join(" ")
                            )}
                        </div>
                    `
                    : ""
                }


                <div class="scheme-footer">

                    <span class="scheme-government">
                        ${escapeHtml(
                            scheme.government ||
                            "Government of India"
                        )}
                    </span>


                    ${
                        scheme.source &&
                        scheme.source.url
                        ? `
                            <a
                                class="scheme-source"
                                href="${escapeAttribute(
                                    scheme.source.url
                                )}"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                Official source →
                            </a>
                        `
                        : ""
                    }

                </div>

            `;


            schemeResultsGrid.appendChild(
                card
            );

        }
    );
}


// ============================================================
// RESET FINDER
// ============================================================

document
    .getElementById(
        "resetFinder"
    )
    .addEventListener(
        "click",
        () => {

            finderForm.reset();

            finderResults.classList.add(
                "hidden"
            );

            window.scrollTo({
                top: 0,
                behavior: "smooth"
            });

        }
    );


// ============================================================
// WELCOME BUTTONS
// ============================================================

function attachWelcomeButtons() {

    document
        .querySelectorAll(
            ".welcome-examples [data-question]"
        )
        .forEach(button => {

            button.addEventListener(
                "click",
                () => {

                    sendChatMessage(
                        button.dataset.question
                    );

                }
            );

        });

}


attachWelcomeButtons();


// ============================================================
// SECURITY HELPERS
// ============================================================

function escapeHtml(
    value
) {

    if (value === null ||
        value === undefined) {

        return "";
    }


    return String(value)
        .replace(
            /&/g,
            "&amp;"
        )
        .replace(
            /</g,
            "&lt;"
        )
        .replace(
            />/g,
            "&gt;"
        )
        .replace(
            /"/g,
            "&quot;"
        )
        .replace(
            /'/g,
            "&#039;"
        );
}


function escapeAttribute(
    value
) {

    return escapeHtml(
        value
    );
}


// ============================================================
// BACKEND HEALTH CHECK
// ============================================================

async function checkBackend() {

    try {

        const response =
            await fetch(
                `${API_BASE}/health`
            );


        if (!response.ok) {
            throw new Error();
        }


        console.log(
            "CivicAI backend connected."
        );


    } catch (error) {

        console.warn(
            "CivicAI backend is not currently reachable."
        );

    }

}


checkBackend();