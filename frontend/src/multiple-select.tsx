import React from 'react';

import Select from 'react-select';

const colourOptions = [
    'red', 'yellow', 'orange', 'purple',
];

export default () => (
    <Select
        defaultValue={[colourOptions[2], colourOptions[3]]}
        isMulti
        name="colors"
        options={colourOptions}
        className="basic-multi-select"
        classNamePrefix="select"
    />
);
