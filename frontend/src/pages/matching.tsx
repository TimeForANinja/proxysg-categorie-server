import React from 'react';
import Select, {StylesConfig} from 'react-select';
import chroma from 'chroma-js';

import {getCategories, ICategory} from "../api/categories";
import {getURLs, IURL} from "../api/urls";
import {colors} from "../api/colormixer";


type ColorOPT = {
    value: number,
    label: string,
    color: string,
}

const mapCategoryToSelectProps = (category: ICategory): ColorOPT => ({
    value: category.id,
    label: category.name,
    color: colors[category.color]
});


function MatchingListPage() {
    const [urls, setURLs] = React.useState<IURL[]>([]);
    const [categories, setCategory] = React.useState<ICategory[]>([]);
    const [expandedId, setExpandedId] = React.useState<number | null>(null);

    const handleExpand = (id: number) => {
        setExpandedId(prevId => prevId === id ? null : id);
    }

    React.useEffect(() => {


        Promise.all([getURLs(), getCategories()])
            .then(([urlsData, categoriesData]) => {
                setURLs(urlsData);
                setCategory(categoriesData);
            })
            .catch((error) => console.error("Error:", error));
    }, []);

    return (
        <table className="table" style={{width: '100%'}}>
            <thead>
            <tr>
                <th>ID</th>
                <th>Hostname</th>
                <th>Categories</th>
                <th>Details</th>
            </tr>
            </thead>
            <tbody>
            {urls.map(url => (
                <React.Fragment key={url.id}>
                    <tr key={url.id}>
                        <td>{url.id}</td>
                        <td>{url.hostname}</td>
                        <td>
                            <Select
                                defaultValue={categories.filter(category => url.categories.includes(category.id)).map(mapCategoryToSelectProps)}
                                isMulti
                                options={categories.map(mapCategoryToSelectProps)}
                                styles={colourStyles}
                            />
                        </td>
                        <td>
                            <button onClick={() => handleExpand(url.id)}>{"<"}</button>
                        </td>
                    </tr>
                    <tr key={url.id + '-expand'} style={{display: expandedId === url.id ? '' : 'none'}}>
                        <td colSpan={99}>Hello there</td>
                    </tr>
                </React.Fragment>
            ))}
            </tbody>
        </table>
    );
}

const colourStyles: StylesConfig<ColorOPT, true> = {
    control: (styles) => ({ ...styles, backgroundColor: 'white' }),
    option: (styles, { data, isDisabled, isFocused, isSelected }) => {
        const color = chroma(data.color);
        return {
            ...styles,
            backgroundColor: isDisabled
                ? undefined
                : isSelected
                    ? data.color
                    : isFocused
                        ? color.alpha(0.1).css()
                        : undefined,
            color: isDisabled
                ? '#ccc'
                : isSelected
                    ? chroma.contrast(color, 'white') > 2
                        ? 'white'
                        : 'black'
                    : data.color,
            cursor: isDisabled ? 'not-allowed' : 'default',

            ':active': {
                ...styles[':active'],
                backgroundColor: !isDisabled
                    ? isSelected
                        ? data.color
                        : color.alpha(0.3).css()
                    : undefined,
            },
        };
    },
    multiValue: (styles, { data }) => {
        const color = chroma(data.color);
        return {
            ...styles,
            backgroundColor: color.alpha(0.1).css(),
        };
    },
    multiValueLabel: (styles, { data }) => ({
        ...styles,
        color: data.color,
    }),
    multiValueRemove: (styles, { data }) => ({
        ...styles,
        color: data.color,
        ':hover': {
            backgroundColor: data.color,
            color: 'white',
        },
    }),
};

export default MatchingListPage;
