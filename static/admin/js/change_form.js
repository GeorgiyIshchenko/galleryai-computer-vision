'use strict';
{
    const inputprojects = ['BUTTON', 'INPUT', 'SELECT', 'TEXTAREA'];
    const modelName = document.getElementById('django-admin-form-add-constants').dataset.modelName;
    if (modelName) {
        const form = document.getElementById(modelName + '_form');
        for (const element of form.elements) {
            // HTMLElement.offsetParent returns null when the element is not
            // rendered.
            if (inputprojects.includes(element.projectName) && !element.disabled && element.offsetParent) {
                element.focus();
                break;
            }
        }
    }
}
