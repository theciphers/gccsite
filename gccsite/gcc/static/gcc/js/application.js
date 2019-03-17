const applicants = document.getElementsByClassName('applicant-head');

function goToApplicant(applicant) {
    // Unfold an applicant's description, and scroll down toward its position
    applicant.show();

    // Scroll to get out of the header
    setTimeout(function() {
        $([document.documentElement, document.body]).animate({
            scrollTop: $(applicant.prev()).offset().top
        }, 0);
    }, 1);
}

/**
 * If there is an anchor to the page, open corresponding applicant and scroll
 * to it.
 */
const url_parts = document.URL.split('#');

if (url_parts.length > 1) {
    const focused_id = url_parts[1];
    const focused_el = $('#' + focused_id);
    goToApplicant(focused_el.next());
}

/**
 * Swap the active status when clicking on an applicant
 */
for (let i = 0 ; i < applicants.length ; i++) {
    applicants[i].addEventListener('click', (event) => {
        const applicant = $(applicants[i]).next();
        applicant.toggle();
    });
}

/**
 * Close all details when hitting escape
 */
document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape')
        for (let i = 0 ; i < applicants.length ; i++)
            $(applicants[i]).next().hide();
});

/**
 * Select next item when pressing `down` arrow
 */
document.addEventListener('keydown', (event) => {
    if (event.key === 'ArrowDown') {
        event.preventDefault();

        let last_opened = -1;

        for (let i = 0 ; i < applicants.length ; i++)
            if ($(applicants[i]).next().is(':visible'))
                last_opened = i;

        if (last_opened != -1)
            $(applicants[last_opened]).next().hide();
        if (last_opened != applicants.length - 1)
            goToApplicant($(applicants[last_opened + 1]).next());
    }
});

/**
 * Select previous item when pressing `up` arrow
 */
document.addEventListener('keydown', (event) => {
    if (event.key === 'ArrowUp') {
        event.preventDefault();

        let last_opened = applicants.length;

        for (let i = applicants.length-1 ; i >= 0 ; i--)
            if ($(applicants[i]).next().is(':visible'))
                last_opened = i;

        if (last_opened != applicants.length)
            $(applicants[last_opened]).next().hide();
        if (last_opened != 0)
            goToApplicant($(applicants[last_opened - 1]).next());
    }
});

/**
 * Enable dropdowns
 */
$('.dropdown-toggle').on('click', function(event) {
    $(`.dropdown-menu[aria-labelledby="${event.target.id}"]`).toggle();
});
