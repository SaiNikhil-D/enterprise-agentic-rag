const API_URL = "http://127.0.0.1:8000";


/* =========================================================
   CHECK API
   ========================================================= */

async function checkAPI() {

    const statusDot =
        document.getElementById(
            "statusDot"
        );

    const statusText =
        document.getElementById(
            "statusText"
        );


    try {

        const response =
            await fetch(
                `${API_URL}/health`
            );


        if (response.ok) {

            statusDot.style.background =
                "#22c55e";

            statusText.textContent =
                "API Online";

        } else {

            throw new Error(
                "API unavailable"
            );

        }

    } catch (error) {

        statusDot.style.background =
            "#ef4444";

        statusText.textContent =
            "API Offline";

    }

}


/* =========================================================
   ASK QUESTION
   ========================================================= */

async function askQuestion() {

    const questionInput =
        document.getElementById(
            "question"
        );

    const askButton =
        document.getElementById(
            "askButton"
        );

    const loading =
        document.getElementById(
            "loading"
        );

    const resultSection =
        document.getElementById(
            "resultSection"
        );


    const question =
        questionInput.value.trim();


    if (!question) {

        alert(
            "Please enter a question."
        );

        return;

    }


    /* -------------------------------------------------------
       UI loading state
       ------------------------------------------------------- */

    askButton.disabled =
        true;

    loading.classList.remove(
        "hidden"
    );

    resultSection.classList.add(
        "hidden"
    );


    try {

        /* ---------------------------------------------------
           API request
           --------------------------------------------------- */

        const response =
            await fetch(
                `${API_URL}/chat`,
                {

                    method:
                        "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body:
                        JSON.stringify({
                            question:
                                question
                        })

                }
            );


        if (!response.ok) {

            throw new Error(
                "API request failed"
            );

        }


        const data =
            await response.json();


        /* ---------------------------------------------------
           Display metadata
           --------------------------------------------------- */

        document.getElementById(
            "agent"
        ).textContent =
            data.agent || "UNKNOWN";


        document.getElementById(
            "verification"
        ).textContent =
            data.verification || "UNKNOWN";


        const confidence =
            data.confidence || 0;


        document.getElementById(
            "confidence"
        ).textContent =
            `${(
                confidence * 100
            ).toFixed(1)}%`;


        document.getElementById(
            "retries"
        ).textContent =
            data.retry_count || 0;


        /* ---------------------------------------------------
           Display answer
           --------------------------------------------------- */

        document.getElementById(
            "answer"
        ).textContent =
            data.answer ||
            "No answer returned.";


        /* ---------------------------------------------------
           Display critic
           --------------------------------------------------- */

        document.getElementById(
            "critic"
        ).textContent =
            data.critique ||
            "No critic feedback available.";


        /* ---------------------------------------------------
           Display sources
           --------------------------------------------------- */

        const sourcesList =
            document.getElementById(
                "sources"
            );


        sourcesList.innerHTML =
            "";


        if (
            data.sources &&
            data.sources.length > 0
        ) {

            data.sources.forEach(
                source => {

                    const li =
                        document.createElement(
                            "li"
                        );

                    li.textContent =
                        source;

                    sourcesList.appendChild(
                        li
                    );

                }
            );

        } else {

            const li =
                document.createElement(
                    "li"
                );

            li.textContent =
                "No sources available.";

            sourcesList.appendChild(
                li
            );

        }


        /* ---------------------------------------------------
           Show result
           --------------------------------------------------- */

        resultSection.classList.remove(
            "hidden"
        );


    } catch (error) {

        console.error(
            error
        );

        alert(
            "Unable to connect to the AI backend. Make sure FastAPI is running."
        );

    } finally {

        askButton.disabled =
            false;

        loading.classList.add(
            "hidden"
        );

    }

}


/* =========================================================
   ENTER KEY
   ========================================================= */

document
    .getElementById("question")
    .addEventListener(
        "keydown",
        function(event) {

            if (
                event.key === "Enter" &&
                !event.shiftKey
            ) {

                event.preventDefault();

                askQuestion();

            }

        }
    );


/* =========================================================
   INITIAL API CHECK
   ========================================================= */

checkAPI();